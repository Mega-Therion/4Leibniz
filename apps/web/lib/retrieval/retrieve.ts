import { pg } from '@/lib/db/client';
import { env } from '@/lib/config';
import { embedQuery, isConfigured } from '@/lib/retrieval/embed';
import type { GuideMode, GuideSource, SearchHit } from '@/lib/types';

export interface RetrievalResult {
  mode: GuideMode;
  sources: GuideSource[];
  degraded: 'ok' | 'unconfigured' | 'error';
}

interface CorpusRow {
  slug: string;
  title: string;
  anchor: string;
  citation_label: string | null;
  excerpt: string;
  section_label: string | null;
  distance: number;
}

interface DossierRow {
  slug: string;
  title: string;
  kind: string;
  excerpt: string;
  distance: number;
}

const SCORE_CUTOFF = 0.55; // cosine distance ceiling — beyond this, evidence is not evidence

/**
 * Retrieval-first context assembly.
 *  1. If a work scope is given, retrieve from that work first.
 *  2. Then broaden to archive-wide corpus retrieval.
 *  3. Always probe the editorial dossier for biography/concept context.
 *  4. Merge, deduplicate, and label the evidence mode.
 */
export async function retrieveContext(
  queryText: string,
  workSlug?: string | null,
): Promise<RetrievalResult> {
  if (!isConfigured()) {
    return { mode: 'insufficient_evidence', sources: [], degraded: 'unconfigured' };
  }

  try {
    const vector = await embedQuery(queryText);
    const vec = JSON.stringify(vector);
    const client = pg();
    const scope = workSlug ?? null;

    const scopedPromise = scope
      ? client<CorpusRow[]>`
          SELECT w.slug, w.title, c.anchor, c.citation_label, c.excerpt,
                 s.label AS section_label,
                 c.embedding <=> ${vec}::vector AS distance
          FROM work_chunks c
          JOIN works w ON w.id = c.work_id
          LEFT JOIN work_sections s ON s.id = c.section_id
          WHERE w.slug = ${scope}
            AND c.embedding <=> ${vec}::vector < ${SCORE_CUTOFF}
          ORDER BY c.embedding <=> ${vec}::vector
          LIMIT ${env.workScopeLimit}`
      : Promise.resolve([] as CorpusRow[]);

    const broadPromise = client<CorpusRow[]>`
      SELECT w.slug, w.title, c.anchor, c.citation_label, c.excerpt,
             s.label AS section_label,
             c.embedding <=> ${vec}::vector AS distance
      FROM work_chunks c
      JOIN works w ON w.id = c.work_id
      LEFT JOIN work_sections s ON s.id = c.section_id
      WHERE (${scope}::text IS NULL OR w.slug <> ${scope})
        AND c.embedding <=> ${vec}::vector < ${SCORE_CUTOFF}
      ORDER BY c.embedding <=> ${vec}::vector
      LIMIT ${env.retrievalLimit}`;

    const dossierPromise = client<DossierRow[]>`
      SELECT d.slug, d.title, d.kind, d.text AS excerpt,
             d.embedding <=> ${vec}::vector AS distance
      FROM dossier_entries d
      WHERE d.embedding <=> ${vec}::vector < ${SCORE_CUTOFF}
      ORDER BY d.embedding <=> ${vec}::vector
      LIMIT 3`;

    const [scoped, broad, dossier] = await Promise.all([
      scopedPromise,
      broadPromise,
      dossierPromise,
    ]);

    const seen = new Set<string>();
    const sources: GuideSource[] = [];

    for (const row of [...scoped, ...broad]) {
      const key = `${row.slug}:${row.anchor}`;
      if (seen.has(key)) continue;
      seen.add(key);
      sources.push({
        kind: 'corpus',
        title: row.title,
        slug: row.slug,
        section: row.section_label ?? row.citation_label ?? null,
        anchor: row.anchor,
        excerpt: row.excerpt,
        score: Math.max(0, 1 - row.distance),
      });
    }
    for (const row of dossier) {
      const key = `dossier:${row.slug}`;
      if (seen.has(key)) continue;
      seen.add(key);
      sources.push({
        kind: 'dossier',
        title: row.title,
        slug: null,
        section: null,
        anchor: null,
        excerpt: row.excerpt.slice(0, 300),
        score: Math.max(0, 1 - row.distance),
      });
    }

    const hasCorpus = sources.some((s) => s.kind === 'corpus');
    const hasDossier = sources.some((s) => s.kind === 'dossier');
    const mode: GuideMode =
      hasCorpus && hasDossier
        ? 'mixed'
        : hasCorpus
          ? 'corpus'
          : hasDossier
            ? 'dossier'
            : 'insufficient_evidence';

    return { mode, sources, degraded: 'ok' };
  } catch (error) {
    console.error('[retrieval] failed:', error);
    return { mode: 'insufficient_evidence', sources: [], degraded: 'error' };
  }
}

/** Semantic archive search — returns ranked hits for the search UI / API. */
export async function searchArchive(
  queryText: string,
  workSlug?: string | null,
  limit = 8,
): Promise<SearchHit[]> {
  if (!isConfigured()) return [];
  const vector = await embedQuery(queryText);
  const vec = JSON.stringify(vector);
  const scope = workSlug ?? null;
  const rows = await pg()<CorpusRow[]>`
    SELECT w.slug, w.title, c.anchor, c.citation_label, c.excerpt,
           s.label AS section_label,
           c.embedding <=> ${vec}::vector AS distance
    FROM work_chunks c
    JOIN works w ON w.id = c.work_id
    LEFT JOIN work_sections s ON s.id = c.section_id
    WHERE (${scope}::text IS NULL OR w.slug = ${scope})
      AND c.embedding <=> ${vec}::vector < 0.7
    ORDER BY c.embedding <=> ${vec}::vector
    LIMIT ${limit}`;
  return rows.map((r) => ({
    workSlug: r.slug,
    workTitle: r.title,
    section: r.section_label ?? r.citation_label ?? null,
    anchor: r.anchor,
    excerpt: r.excerpt,
    score: Math.max(0, 1 - r.distance),
  }));
}
