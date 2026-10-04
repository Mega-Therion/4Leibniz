import { StatusBadge, ThemeBadge } from '@/components/ThemeBadge';
import Link from 'next/link';
import type { Work } from '@/lib/types';

interface WorkMetadataPanelProps {
  work: Work;
  themeLabels: Map<string, string>;
  relatedWorks: { slug: string; title: string }[];
  relatedConcepts: { slug: string; term: string }[];
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="label">{label}</dt>
      <dd className="mt-1 text-sm leading-relaxed text-text2">{children}</dd>
    </div>
  );
}

export function WorkMetadataPanel({
  work,
  themeLabels,
  relatedWorks,
  relatedConcepts,
}: WorkMetadataPanelProps) {
  return (
    <aside className="flex flex-col gap-s6" aria-label="Work metadata">
      <div className="panel p-s6">
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={work.status} />
          <ThemeBadge label={work.language.toUpperCase()} />
          {work.originalLanguage && (
            <ThemeBadge label={`orig. ${work.originalLanguage.toUpperCase()}`} />
          )}
        </div>
        <dl className="mt-s6 flex flex-col gap-s4">
          {work.altTitle && <Field label="Original title">{work.altTitle}</Field>}
          <Field label="Composed">{work.dateLabel}</Field>
          {work.translator && <Field label="Translator">{work.translator}</Field>}
          <Field label="Sections">{work.sections.length} anchored sections</Field>
          <Field label="Text length">
            {(work.charCount / 1000).toFixed(1)}k characters, indexed
          </Field>
        </dl>
      </div>

      <div className="panel p-s6">
        <p className="label">Provenance</p>
        <p className="mt-s3 text-sm leading-relaxed text-text2">{work.sourceNote}</p>
        <p className="label mt-s6">Editorial note</p>
        <p className="mt-s3 text-sm leading-relaxed text-text2">{work.editorialNote}</p>
      </div>

      {work.themes.length > 0 && (
        <div className="panel p-s6">
          <p className="label">Themes</p>
          <div className="mt-s3 flex flex-wrap gap-2">
            {work.themes.map((slug) => (
              <ThemeBadge key={slug} label={themeLabels.get(slug) ?? slug} variant="gold" />
            ))}
          </div>
        </div>
      )}

      {relatedConcepts.length > 0 && (
        <div className="panel p-s6">
          <p className="label">Related concepts</p>
          <ul className="mt-s3 flex flex-col gap-2 text-sm">
            {relatedConcepts.map((c) => (
              <li key={c.slug}>
                <Link
                  href={`/leibniz/concepts#${c.slug}`}
                  className="text-text2 underline decoration-gold2 underline-offset-4 hover:text-gold1"
                >
                  {c.term}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {relatedWorks.length > 0 && (
        <div className="panel p-s6">
          <p className="label">Related works</p>
          <ul className="mt-s3 flex flex-col gap-2 text-sm">
            {relatedWorks.map((w) => (
              <li key={w.slug}>
                <Link
                  href={`/works/${w.slug}`}
                  className="text-text2 underline decoration-gold2 underline-offset-4 hover:text-gold1"
                >
                  {w.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      <Link
        href={`/guide?work=${work.slug}`}
        className="btn-gold justify-center text-center"
      >
        Ask the guide about this work
      </Link>
    </aside>
  );
}
