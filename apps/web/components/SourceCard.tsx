import Link from 'next/link';
import type { GuideSource } from '@/lib/types';

/**
 * A retrieved evidence card. Corpus sources deep-link to the exact
 * section anchor; dossier sources are labeled editorial background.
 */
export function SourceCard({ source, index }: { source: GuideSource; index: number }) {
  const isCorpus = source.kind === 'corpus';
  return (
    <li className="panel-flat p-s4">
      <div className="flex items-baseline justify-between gap-s3">
        <span className="chip chip-gold !py-0.5 !text-[10px]">
          {isCorpus ? 'Corpus' : 'Dossier'}
        </span>
        <span className="font-mono text-[10px] text-text3">[{index + 1}]</span>
      </div>
      {isCorpus && source.slug ? (
        <Link
          href={`/works/${source.slug}#${source.anchor}`}
          className="mt-s3 block text-sm text-text1 underline decoration-gold2 underline-offset-4 hover:text-gold1"
        >
          {source.title}
          {source.section ? ` — ${source.section}` : ''}
        </Link>
      ) : (
        <p className="mt-s3 text-sm text-text1">
          {source.title}
          <span className="text-text3"> · editorial background</span>
        </p>
      )}
      <p className="mt-s2 line-clamp-3 text-xs leading-relaxed text-text3">
        “{source.excerpt}”
      </p>
    </li>
  );
}
