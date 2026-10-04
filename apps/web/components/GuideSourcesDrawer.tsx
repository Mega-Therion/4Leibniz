'use client';

import { useState } from 'react';
import { SourceCard } from '@/components/SourceCard';
import type { GuideSource } from '@/lib/types';

/**
 * Collapsible citations drawer — the evidence behind an answer.
 */
export function GuideSourcesDrawer({
  sources,
}: {
  sources: GuideSource[];
}) {
  const [open, setOpen] = useState(false);
  if (sources.length === 0) return null;

  return (
    <div className="mt-s4">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="chip chip-gold transition-colors hover:border-gold1"
      >
        <svg
          width="10"
          height="10"
          viewBox="0 0 10 10"
          fill="none"
          aria-hidden="true"
          className={`transition-transform ${open ? 'rotate-90' : ''}`}
        >
          <path d="M3 1l4 4-4 4" stroke="currentColor" strokeWidth="1.4" />
        </svg>
        {sources.length} {sources.length === 1 ? 'source' : 'sources'}
      </button>
      {open && (
        <ul className="mt-s3 grid gap-2 sm:grid-cols-2" aria-label="Sources">
          {sources.map((source, i) => (
            <SourceCard key={`${source.title}-${i}`} source={source} index={i} />
          ))}
        </ul>
      )}
    </div>
  );
}
