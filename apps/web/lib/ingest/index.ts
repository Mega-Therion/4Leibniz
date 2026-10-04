import { eq } from 'drizzle-orm';
import { db } from '@/lib/db/client';
import * as t from '@/lib/db/schema';
import { chunkWork, type ChunkDraft } from '@/lib/ingest/chunker';
import { loadDossier, loadWorksForIngest } from '@/lib/ingest/loader';
import { embedBatch } from '@/lib/retrieval/embed';

export interface IngestReport {
  works: number;
  sections: number;
  chunks: number;
  dossierEntries: number;
  themes: number;
  entities: number;
}

interface WorkRow {
  id: string;
  slug: string;
  title: string;
}

const slugify = (value: string) =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');

/**
 * Full corpus ingestion: works → sections → chunks → embeddings, plus
 * themes, entities, and the editorial dossier. Idempotent — safe to re-run.
 */
export async function runIngestion(): Promise<IngestReport> {
  const database = db();
  const worksData = await loadWorksForIngest();
  const dossier = await loadDossier();

  const report: IngestReport = {
    works: 0,
    sections: 0,
    chunks: 0,
    dossierEntries: 0,
    themes: 0,
    entities: 0,
  };

  // ── Themes ────────────────────────────────────────────────────────────
  const themeIdBySlug = new Map<string, string>();
  for (const theme of dossier.themes) {
    const [row] = await database
      .insert(t.themes)
      .values({
        slug: theme.slug,
        label: theme.label,
        description: theme.description,
      })
      .onConflictDoUpdate({
        target: t.themes.slug,
        set: { label: theme.label, description: theme.description },
      })
      .returning({ id: t.themes.id });
    themeIdBySlug.set(theme.slug, row.id);
    report.themes += 1;
  }

  // ── Entities (persons) ──────────────────────────────────────────────────
  const entityIdByName = new Map<string, { id: string; name: string; slug: string }>();
  const entityNames = new Set<string>([
    ...dossier.correspondents.map((c: { name: string }) => c.name),
    ...worksData.flatMap((w) => w.meta.entities ?? []),
  ]);
  for (const name of entityNames) {
    const slug = slugify(name);
    const [row] = await database
      .insert(t.entities)
      .values({ slug, name, kind: 'person' })
      .onConflictDoUpdate({ target: t.entities.slug, set: { name } })
      .returning({ id: t.entities.id });
    entityIdByName.set(name, { id: row.id, name, slug });
    report.entities += 1;
  }

  // ── Works, sections, chunks ─────────────────────────────────────────────
  const workIdBySlug = new Map<string, string>();

  for (const work of worksData) {
    const meta = work.meta;
    const [workRow] = await database
      .insert(t.works)
      .values({
        slug: meta.slug,
        title: meta.title,
        altTitle: meta.altTitle ?? null,
        summary: meta.summary ?? '',
        language: meta.language ?? 'en',
        originalLanguage: meta.originalLanguage ?? null,
        status: meta.status ?? 'in-progress',
        dateLabel: meta.dateLabel ?? null,
        dateStart: meta.dateStart ?? null,
        dateEnd: meta.dateEnd ?? null,
        sourceNote: meta.sourceNote ?? null,
        editorialNote: meta.editorialNote ?? null,
        featured: Boolean(meta.featured),
        published: meta.published !== false,
      })
      .onConflictDoUpdate({
        target: t.works.slug,
        set: {
          title: meta.title,
          summary: meta.summary ?? '',
          updatedAt: new Date(),
        },
      })
      .returning({ id: t.works.id });

    const row = workRow as WorkRow;
    workIdBySlug.set(meta.slug, row.id);

    // reset sections + chunks for this work (idempotent re-index)
    await database.delete(t.workChunks).where(eq(t.workChunks.workId, row.id));
    await database.delete(t.workSections).where(eq(t.workSections.workId, row.id));

    // work ↔ themes
    for (const themeSlug of meta.themes ?? []) {
      const themeId = themeIdBySlug.get(themeSlug);
      if (!themeId) continue;
      await database
        .insert(t.workThemes)
        .values({ workId: row.id, themeId })
        .onConflictDoNothing();
    }

    const sectionIdByAnchor = new Map<string, string>();
    for (const [i, section] of work.sections.entries()) {
      const [sectionRow] = await database
        .insert(t.workSections)
        .values({
          workId: row.id,
          anchor: section.anchor,
          label: section.label,
          title: section.title,
          position: i,
        })
        .returning({ id: t.workSections.id });
      sectionIdByAnchor.set(section.anchor, sectionRow.id);
      report.sections += 1;
    }

    const drafts: ChunkDraft[] = chunkWork({
      title: meta.title,
      sections: work.sections,
    });

    if (drafts.length > 0) {
      const embeddings = await embedBatch(drafts.map((d) => d.text));
      for (const [i, draft] of drafts.entries()) {
        const [chunkRow] = await database
          .insert(t.workChunks)
          .values({
            workId: row.id,
            sectionId: sectionIdByAnchor.get(draft.anchor) ?? null,
            anchor: draft.anchor,
            text: draft.text,
            excerpt: draft.excerpt,
            embedding: embeddings[i],
            charCount: draft.charCount,
            tokenEstimate: draft.tokenEstimate,
            language: meta.language ?? 'en',
            qualityScore: 0.9,
            citationLabel: draft.citationLabel,
          })
          .returning({ id: t.workChunks.id });

        // attach entities mentioned in this chunk
        for (const [, entity] of entityIdByName) {
          if (draft.text.includes(entity.name)) {
            await database
              .insert(t.chunkEntities)
              .values({ chunkId: chunkRow.id, entityId: entity.id })
              .onConflictDoNothing();
          }
        }
        report.chunks += 1;
      }
    }
    report.works += 1;
  }

  // ── Dossier ────────────────────────────────────────────────────────────
  report.dossierEntries = await seedDossier(database);
  return report;
}

type Database = ReturnType<typeof db>;

export async function seedDossier(database?: Database): Promise<number> {
  const d = database ?? db();
  const dossier = await loadDossier();

  const entries: { kind: string; slug: string; title: string; text: string; metadata?: Record<string, unknown> }[] = [];

  // biography — one entry per paragraph
  const bioParagraphs = dossier.biography
    .split('\n\n')
    .map((p: string) => p.replace(/^#+\s*/, '').trim())
    .filter(Boolean);
  bioParagraphs.forEach((paragraph: string, i: number) => {
    entries.push({
      kind: 'biography',
      slug: `biography-${i + 1}`,
      title: 'Leibniz — Editorial Biography',
      text: paragraph,
    });
  });

  for (const event of dossier.timeline) {
    entries.push({
      kind: 'timeline',
      slug: event.slug,
      title: `${event.dateLabel} — ${event.title}`,
      text: `${event.title} (${event.dateLabel}). ${event.description}`,
      metadata: { year: event.year, category: event.category },
    });
  }

  for (const concept of dossier.concepts) {
    entries.push({
      kind: 'concept',
      slug: concept.slug,
      title: concept.term,
      text: `${concept.short}. ${concept.definition}`,
    });
  }

  for (const correspondent of dossier.correspondents) {
    entries.push({
      kind: 'correspondent',
      slug: correspondent.slug,
      title: correspondent.name,
      text: `${correspondent.name} (${correspondent.dates}) — ${correspondent.relation}. ${correspondent.summary}`,
    });
  }

  for (const theme of dossier.themes) {
    entries.push({
      kind: 'theme',
      slug: theme.slug,
      title: theme.label,
      text: theme.description,
    });
  }

  await d.delete(t.dossierEntries);
  const embeddings = await embedBatch(entries.map((e) => e.text));
  for (const [i, entry] of entries.entries()) {
    await d.insert(t.dossierEntries).values({
      kind: entry.kind,
      slug: entry.slug,
      title: entry.title,
      text: entry.text,
      metadata: entry.metadata ?? null,
      embedding: embeddings[i],
    });
  }

  // timeline_events table (structured, non-vector)
  await d.delete(t.timelineEvents);
  for (const event of dossier.timeline) {
    await d.insert(t.timelineEvents).values({
      slug: event.slug,
      year: event.year,
      dateLabel: event.dateLabel,
      title: event.title,
      description: event.description,
      category: event.category,
    });
  }

  return entries.length;
}
