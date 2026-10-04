import Link from 'next/link';
import { StatusBadge, ThemeBadge } from '@/components/ThemeBadge';
import type { ArchiveWork } from '@/lib/types';

const STATUS_LABEL: Record<string, string> = {
  translated: 'Translated',
  transcribed: 'Transcribed',
  completed: 'Completed edition',
  'in-progress': 'In progress',
};

export function WorkCard({ work, themes }: { work: ArchiveWork; themes: Map<string, string> }) {
  return (
    <Link
      href={`/works/${work.slug}`}
      className="panel group relative flex flex-col gap-s4 p-s6 transition-transform duration-300 hover:-translate-y-1"
    >
      <div className="flex items-start justify-between gap-s4">
        <div>
          <p className="label">{work.dateLabel}</p>
          <h3 className="serif-heading mt-s2 text-2xl text-text1 group-hover:text-gold1">
            {work.title}
          </h3>
          {work.altTitle && (
            <p className="mt-1 text-sm italic text-text3">{work.altTitle}</p>
          )}
        </div>
        <StatusBadge status={work.status} />
      </div>

      <p className="line-clamp-4 text-sm leading-relaxed text-text2">{work.summary}</p>

      <div className="mt-auto flex flex-wrap items-center gap-2 pt-s2">
        <ThemeBadge label={work.language.toUpperCase()} variant="plain" />
        {work.originalLanguage && (
          <ThemeBadge label={`orig. ${work.originalLanguage.toUpperCase()}`} variant="plain" />
        )}
        {work.themes.slice(0, 3).map((slug) => (
          <ThemeBadge
            key={slug}
            label={themes.get(slug) ?? slug}
            variant="gold"
          />
        ))}
      </div>

      <span className="label text-right text-gold1 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        {work.sectionCount} sections · read →
      </span>
      <span className="sr-only">{STATUS_LABEL[work.status]}</span>
    </Link>
  );
}
