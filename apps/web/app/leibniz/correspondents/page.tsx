import type { Metadata } from 'next';
import { SectionFrame } from '@/components/SectionFrame';
import { CorrespondentCard } from '@/components/CorrespondentCard';
import { getCorrespondents } from '@/lib/content';
import type { Correspondent } from '@/lib/types';

export const metadata: Metadata = {
  title: 'Correspondents',
  description:
    "Leibniz's letter network: Arnauld, Clarke, Sophia of Hanover, the Bernoullis, Wolff, Des Bosses — the correspondents behind the philosophy.",
  alternates: { canonical: '/leibniz/correspondents' },
};

export default async function CorrespondentsPage() {
  const correspondents = (await getCorrespondents()) as Correspondent[];

  return (
    <SectionFrame
      eyebrow="Dossier · Correspondents"
      title="The letter network."
      description="Over a thousand letters survive. These are the minds across the table — the people whose objections made the system sharper."
      className="pt-s12"
    >
      <div className="grid gap-s6 lg:grid-cols-2">
        {correspondents.map((person) => (
          <CorrespondentCard key={person.slug} correspondent={person} />
        ))}
      </div>
    </SectionFrame>
  );
}
