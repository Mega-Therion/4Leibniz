// ─── 4Leibniz shared types ────────────────────────────────────────────────

export type WorkStatus =
  | 'transcribed'
  | 'translated'
  | 'completed'
  | 'in-progress';

export interface WorkMeta {
  slug: string;
  title: string;
  altTitle?: string;
  language: string;
  originalLanguage?: string;
  status: WorkStatus;
  dateLabel: string;
  dateStart?: number;
  dateEnd?: number;
  translator?: string;
  summary: string;
  sourceNote: string;
  editorialNote: string;
  featured: boolean;
  published: boolean;
  themes: string[];
  relatedConcepts: string[];
  entities?: string[];
}

export interface WorkSection {
  label: string;
  title: string | null;
  anchor: string;
  paragraphs: string[];
}

export interface Work extends WorkMeta {
  sections: WorkSection[];
  hasOriginal: boolean;
  charCount: number;
}

export interface DossierEntry {
  kind: 'biography' | 'timeline' | 'concept' | 'correspondent' | 'theme';
  slug: string;
  title: string;
  text: string;
}

export interface TimelineEvent {
  slug: string;
  year: number;
  dateLabel: string;
  title: string;
  description: string;
  category: 'life' | 'work' | 'science' | 'diplomacy' | 'legacy';
}

export interface Concept {
  slug: string;
  term: string;
  short: string;
  definition: string;
  relatedWorks: string[];
  relatedConcepts: string[];
}

export interface Correspondent {
  slug: string;
  name: string;
  dates: string;
  relation: string;
  summary: string;
}

export interface Theme {
  slug: string;
  label: string;
  description: string;
  works: string[];
}

export interface ArchiveWork {
  slug: string;
  title: string;
  altTitle?: string;
  language: string;
  originalLanguage?: string;
  status: WorkStatus;
  dateLabel: string;
  dateStart?: number;
  summary: string;
  themes: string[];
  sectionCount: number;
  charCount: number;
  featured: boolean;
}

// ─── AI guide contract ───────────────────────────────────────────────────

export type GuideMode = 'corpus' | 'dossier' | 'mixed' | 'insufficient_evidence';

export interface GuideSource {
  kind: 'corpus' | 'dossier';
  title: string;
  slug: string | null;
  section: string | null;
  anchor: string | null;
  excerpt: string;
  score?: number;
}

export interface GuideData {
  mode: GuideMode;
  sources: GuideSource[];
  suggestedFollowups: string[];
  scope?: string | null;
  /** Catalogued formal claims matched from the user's message (contract v1). */
  formal_claims?: import('@/lib/formal-claims').ClaimDisplay[];
}

export interface SearchHit {
  workSlug: string;
  workTitle: string;
  section: string | null;
  anchor: string | null;
  excerpt: string;
  score: number;
}
