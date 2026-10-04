import type { Correspondent } from '@/lib/types';

export function CorrespondentCard({ correspondent }: { correspondent: Correspondent }) {
  const initials = correspondent.name
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('');

  return (
    <article className="panel flex gap-s4 p-s6">
      <div
        aria-hidden="true"
        className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-line1 font-serif text-sm text-gold1"
        style={{ fontFamily: 'var(--font-display)' }}
      >
        {initials}
      </div>
      <div>
        <h3 className="serif-heading text-xl text-text1">{correspondent.name}</h3>
        <p className="mt-1 font-mono text-xs text-text3">
          {correspondent.dates} · {correspondent.relation}
        </p>
        <p className="mt-s3 text-sm leading-relaxed text-text2">
          {correspondent.summary}
        </p>
      </div>
    </article>
  );
}
