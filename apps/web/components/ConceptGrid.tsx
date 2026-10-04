'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import type { Concept } from '@/lib/types';

/** Concepts glossary grid with a live letter/theme filter. */
export function ConceptGrid({ concepts }: { concepts: Concept[] }) {
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return concepts;
    return concepts.filter((c) =>
      `${c.term} ${c.short} ${c.definition}`.toLowerCase().includes(q),
    );
  }, [concepts, query]);

  return (
    <div>
      <label className="flex max-w-md flex-col gap-1">
        <span className="label">Filter concepts</span>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. harmony, force, windows…"
          className="panel-flat px-s3 py-2 text-sm text-text1 placeholder:text-text3"
          style={{ background: 'var(--bg-1)' }}
        />
      </label>

      <p className="mt-s4 text-sm text-text3" role="status">
        {filtered.length} of {concepts.length} concepts
      </p>

      <div className="mt-s6 grid gap-s6 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((concept) => (
          <article
            key={concept.slug}
            id={concept.slug}
            className="panel flex flex-col gap-s3 p-s6 scroll-mt-28"
          >
            <h3 className="serif-heading text-2xl text-text1">{concept.term}</h3>
            <p className="text-sm italic text-gold1">{concept.short}</p>
            <p className="text-sm leading-relaxed text-text2">{concept.definition}</p>

            {concept.relatedWorks.length > 0 && (
              <div className="mt-auto pt-s4">
                <p className="label">Appears in</p>
                <ul className="mt-s2 flex flex-wrap gap-2">
                  {concept.relatedWorks.map((slug) => (
                    <li key={slug}>
                      <Link
                        href={`/works/${slug}`}
                        className="chip chip-gold hover:border-gold1"
                      >
                        {slug === 'discourse-on-metaphysics'
                          ? 'Discourse'
                          : slug === 'monadology'
                            ? 'Monadology'
                            : slug}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {concept.relatedConcepts.length > 0 && (
              <div className="pt-s2">
                <p className="label">Connects to</p>
                <ul className="mt-s2 flex flex-wrap gap-2">
                  {concept.relatedConcepts.map((slug) => (
                    <li key={slug}>
                      <a href={`#${slug}`} className="chip chip-violet">
                        {slug.replace(/-/g, ' ')}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </article>
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="mt-s6 text-sm text-text3">
          No concept matches that filter — the dossier is small but exacting.
        </p>
      )}
    </div>
  );
}
