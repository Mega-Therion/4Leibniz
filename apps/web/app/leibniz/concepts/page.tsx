import type { Metadata } from 'next';
import { SectionFrame } from '@/components/SectionFrame';
import { ConceptGrid } from '@/components/ConceptGrid';
import { getConcepts } from '@/lib/content';
import type { Concept } from '@/lib/types';

export const metadata: Metadata = {
  title: 'Concepts',
  description:
    'The Leibniz glossary: monads, pre-established harmony, sufficient reason, vis viva, the universal characteristic — each defined and linked to its texts.',
  alternates: { canonical: '/leibniz/concepts' },
};

export default async function ConceptsPage() {
  const concepts = (await getConcepts()) as Concept[];

  return (
    <SectionFrame
      eyebrow="Dossier · Concepts"
      title="The glossary."
      description="Editorial definitions, cross-linked across concepts and works. The guide reads this layer as background — never as quotation."
      className="pt-s12"
    >
      <ConceptGrid concepts={concepts} />
    </SectionFrame>
  );
}
