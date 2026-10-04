import { promises as fs } from 'fs';
import path from 'path';
import { parseWorkText } from '@/lib/content-shared';
import type { WorkMeta } from '@/lib/types';

const CONTENT_ROOT = path.join(process.cwd(), 'content');
const WORKS_ROOT = path.join(CONTENT_ROOT, 'works');
const DOSSIER_ROOT = path.join(CONTENT_ROOT, 'dossier');

export interface IngestWork {
  meta: WorkMeta;
  sections: ReturnType<typeof parseWorkText>;
}

export async function loadWorksForIngest(): Promise<IngestWork[]> {
  const entries = await fs.readdir(WORKS_ROOT, { withFileTypes: true });
  const works: IngestWork[] = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const dir = path.join(WORKS_ROOT, entry.name);
    try {
      const [metaRaw, text] = await Promise.all([
        fs.readFile(path.join(dir, 'meta.json'), 'utf8'),
        fs.readFile(path.join(dir, 'text.en.md'), 'utf8'),
      ]);
      works.push({
        meta: JSON.parse(metaRaw) as WorkMeta,
        sections: parseWorkText(text),
      });
    } catch {
      // skip malformed/incomplete work folders
    }
  }
  return works;
}

export async function loadDossier() {
  const [biography, timelineRaw, conceptsRaw, correspondentsRaw, themesRaw] =
    await Promise.all([
      fs.readFile(path.join(DOSSIER_ROOT, 'biography.md'), 'utf8'),
      fs.readFile(path.join(DOSSIER_ROOT, 'timeline.json'), 'utf8'),
      fs.readFile(path.join(DOSSIER_ROOT, 'concepts.json'), 'utf8'),
      fs.readFile(path.join(DOSSIER_ROOT, 'correspondents.json'), 'utf8'),
      fs.readFile(path.join(DOSSIER_ROOT, 'themes.json'), 'utf8'),
    ]);
  return {
    biography,
    timeline: JSON.parse(timelineRaw),
    concepts: JSON.parse(conceptsRaw),
    correspondents: JSON.parse(correspondentsRaw),
    themes: JSON.parse(themesRaw),
  };
}
