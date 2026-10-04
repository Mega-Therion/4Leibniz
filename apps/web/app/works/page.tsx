import type { Metadata } from 'next';
import { SectionFrame } from '@/components/SectionFrame';
import { ArchiveExplorer } from '@/components/ArchiveExplorer';
import type { ArchiveWork } from '@/lib/types';
import { getWorks, getThemes } from '@/lib/content';

export const metadata: Metadata = {
  title: 'The Archive',
  description:
    'Browse the 4Leibniz archive: transcribed and translated works of Leibniz, with status, language, themes, and editorial abstracts.',
  alternates: { canonical: '/works' },
};

export default async function WorksPage() {
  const [works, themes] = await Promise.all([getWorks(), getThemes()]);
  const themeLabels = new Map(
    (themes as { slug: string; label: string }[]).map((t) => [t.slug, t.label]),
  );

  const slim: ArchiveWork[] = works.map((w) => ({
    slug: w.slug,
    title: w.title,
    altTitle: w.altTitle,
    language: w.language,
    originalLanguage: w.originalLanguage,
    status: w.status,
    dateLabel: w.dateLabel,
    dateStart: w.dateStart,
    summary: w.summary,
    themes: w.themes,
    sectionCount: w.sections.length,
    charCount: w.charCount,
    featured: w.featured,
  }));

  return (
    <SectionFrame
      eyebrow="The archive"
      title="Every work, anchored."
      description="Filter by status, language, and theme — or search the editorial abstracts. Each work opens as a digital scholarly edition with stable section anchors and a scoped AI guide."
      className="pt-s12"
    >
      <ArchiveExplorer works={slim} themeLabels={themeLabels} />
    </SectionFrame>
  );
}
