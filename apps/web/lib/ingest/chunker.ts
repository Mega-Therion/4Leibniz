import type { ParsedSection } from '@/lib/content-shared';

export interface ChunkDraft {
  section: ParsedSection;
  anchor: string;
  label: string;
  text: string;
  excerpt: string;
  citationLabel: string;
  charCount: number;
  tokenEstimate: number;
}

const MAX_CHARS = 1400;

function makeExcerpt(text: string): string {
  const clean = text.replace(/\s+/g, ' ').trim();
  return clean.length <= 260 ? clean : `${clean.slice(0, 257)}…`;
}

/**
 * Splits a work into semantically useful chunks.
 * Chunks never cross section boundaries and preserve the section anchor,
 * so every retrieved passage can be cited to a stable subsection of the work.
 */
export function chunkWork(work: { title: string; sections: ParsedSection[] }): ChunkDraft[] {
  const chunks: ChunkDraft[] = [];

  for (const section of work.sections) {
    let buffer: string[] = [];
    let bufferChars = 0;

    const flush = () => {
      if (buffer.length === 0) return;
      const text = buffer.join('\n\n');
      const label = section.title
        ? `§${section.label} — ${section.title}`
        : `§${section.label}`;
      chunks.push({
        section,
        anchor: section.anchor,
        label,
        text,
        excerpt: makeExcerpt(text),
        citationLabel: `${work.title} §${section.label}`,
        charCount: text.length,
        tokenEstimate: Math.ceil(text.length / 4),
      });
      buffer = [];
      bufferChars = 0;
    };

    for (const paragraph of section.paragraphs) {
      // A single very long paragraph becomes its own chunk.
      if (paragraph.length >= MAX_CHARS) {
        flush();
        buffer = [paragraph];
        bufferChars = paragraph.length;
        flush();
        continue;
      }
      if (bufferChars + paragraph.length > MAX_CHARS) {
        flush();
      }
      buffer.push(paragraph);
      bufferChars += paragraph.length + 2;
    }
    flush();
  }

  return chunks;
}
