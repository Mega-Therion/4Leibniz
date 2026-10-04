import type { Metadata } from 'next';
import { SectionFrame } from '@/components/SectionFrame';
import { TimelineRail } from '@/components/TimelineRail';
import { getTimeline } from '@/lib/content';
import type { TimelineEvent } from '@/lib/types';

export const metadata: Metadata = {
  title: 'Timeline',
  description:
    'The life and works of Leibniz on one rail: Leipzig to Hanover, the calculus to the Monadology, 1646–1765.',
  alternates: { canonical: '/leibniz/timeline' },
};

export default async function TimelinePage() {
  const events = (await getTimeline()) as TimelineEvent[];

  return (
    <SectionFrame
      eyebrow="Dossier · Timeline"
      title="Seventy years, one rail."
      description="Life, works, science, diplomacy, and legacy — the editorial spine of the archive."
      className="pt-s12"
    >
      <div className="mx-auto max-w-3xl">
        <TimelineRail events={events} />
      </div>
    </SectionFrame>
  );
}
