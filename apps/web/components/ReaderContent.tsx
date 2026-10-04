'use client';

import { useState } from 'react';
import type { Work } from '@/lib/types';

/**
 * Renders the edition text. If a parallel original (text.orig.md) is
 * ingested for the work, a side-by-side toggle becomes available.
 */
export function ReaderContent({ work }: { work: Work }) {
  const [bilingual, setBilingual] = useState(false);
  const hasOriginal = work.hasOriginal;

  return (
    <div>
      {hasOriginal && (
        <div className="mb-s8 flex items-center gap-s3">
          <button
            type="button"
            onClick={() => setBilingual((v) => !v)}
            aria-pressed={bilingual}
            className="btn-ghost !px-4 !py-1.5 text-xs"
          >
            {bilingual ? 'English only' : 'Side-by-side original'}
          </button>
          <span className="text-xs text-text3">
            Parallel view — translation and original aligned by section.
          </span>
        </div>
      )}

      <div className={bilingual ? 'grid gap-s8 lg:grid-cols-2' : ''}>
        <article className="reader-prose" lang={work.language}>
          {work.sections.map((section) => (
            <section
              key={section.anchor}
              id={section.anchor}
              className="mb-s12 scroll-mt-28"
              aria-label={`Section ${section.label}`}
            >
              <header className="mb-s4">
                <div className="flex items-baseline gap-s3">
                  <span className="font-mono text-sm text-gold2">§{section.label}</span>
                  {section.title && (
                    <h2 className="serif-heading text-xl text-text1 sm:text-2xl">
                      {section.title}
                    </h2>
                  )}
                </div>
                <div className="gold-rule mt-s3 w-16" />
              </header>
              {section.paragraphs.map((p, j) => (
                <p key={j}>{p}</p>
              ))}
            </section>
          ))}
        </article>

        {bilingual && hasOriginal && (
          <article
            className="reader-prose border-l border-line1 pl-s6"
            lang={work.originalLanguage}
          >
            <p className="label mb-s4">
              Original — {work.originalLanguage?.toUpperCase()}
            </p>
            <p className="text-sm text-text3">
              Parallel original pending section alignment for this work. See the
              editorial note for status.
            </p>
          </article>
        )}
      </div>
    </div>
  );
}
