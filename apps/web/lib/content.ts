import 'server-only';
import { promises as fs } from 'fs';
import path from 'path';
import { parseWorkText } from '@/lib/content-shared';
import type { Work, WorkMeta } from '@/lib/types';

const CONTENT_ROOT = path.join(process.cwd(), 'content');
const WORKS_ROOT = path.join(CONTENT_ROOT, 'works');

function parseOriginalPresence(dir: string): Promise<boolean> {
  return fs
    .access(path.join(dir, 'text.orig.md'))
    .then(() => true)
    .catch(() => false);
}

async function loadWork(dirName: string): Promise<Work | null> {
  const dir = path.join(WORKS_ROOT, dirName);
  try {
    const [metaRaw, text] = await Promise.all([
      fs.readFile(path.join(dir, 'meta.json'), 'utf8'),
      fs.readFile(path.join(dir, 'text.en.md'), 'utf8'),
    ]);
    const meta = JSON.parse(metaRaw) as WorkMeta;
    const sections = parseWorkText(text);
    const hasOriginal = await parseOriginalPresence(dir);
    return {
      ...meta,
      sections,
      hasOriginal,
      charCount: text.length,
    };
  } catch {
    return null;
  }
}

let worksCache: Work[] | null = null;

export async function getWorks(): Promise<Work[]> {
  if (worksCache) return worksCache;
  const entries = await fs.readdir(WORKS_ROOT, { withFileTypes: true });
  const dirs = entries.filter((e) => e.isDirectory()).map((e) => e.name);
  const loaded = await Promise.all(dirs.map(loadWork));
  worksCache = loaded
    .filter((w): w is Work => w !== null && w.published)
    .sort((a, b) => (a.dateStart ?? 0) - (b.dateStart ?? 0));
  return worksCache;
}

export async function getWork(slug: string): Promise<Work | null> {
  const works = await getWorks();
  return works.find((w) => w.slug === slug) ?? null;
}

// ─── Dossier ──────────────────────────────────────────────────────────────

const dossierRoot = path.join(CONTENT_ROOT, 'dossier');

export async function getBiography(): Promise<string[]> {
  const md = await fs.readFile(path.join(dossierRoot, 'biography.md'), 'utf8');
  return md
    .split('\n\n')
    .map((p) => p.replace(/^#+\s*/, '').trim())
    .filter(Boolean);
}

export async function getTimeline() {
  const raw = await fs.readFile(path.join(dossierRoot, 'timeline.json'), 'utf8');
  return JSON.parse(raw);
}

export async function getConcepts() {
  const raw = await fs.readFile(path.join(dossierRoot, 'concepts.json'), 'utf8');
  return JSON.parse(raw);
}

export async function getCorrespondents() {
  const raw = await fs.readFile(path.join(dossierRoot, 'correspondents.json'), 'utf8');
  return JSON.parse(raw);
}

export async function getThemes() {
  const raw = await fs.readFile(path.join(dossierRoot, 'themes.json'), 'utf8');
  return JSON.parse(raw);
}
