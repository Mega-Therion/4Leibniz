import type { Metadata } from 'next';
import { GuidePanel } from '@/components/GuidePanel';
import { getWorks } from '@/lib/content';

export const metadata: Metadata = {
  title: 'The Guide',
  description:
    'Ask the 4Leibniz Guide: a retrieval-grounded AI that answers from the archive texts and editorial dossier, with cited sources you can verify.',
  alternates: { canonical: '/guide' },
};

interface PageProps {
  searchParams: Promise<{ work?: string; q?: string }>;
}

export default async function GuidePage({ searchParams }: PageProps) {
  const { work: workParam, q } = await searchParams;
  const works = await getWorks();
  const workSlug = workParam ?? null;
  const scopedWork = works.find((w) => w.slug === workSlug) ?? null;

  return (
    <div className="mx-auto max-w-3xl px-s6 pt-s12">
      <header className="mb-s8">
        <p className="label">The guide</p>
        <h1 className="serif-heading mt-s3 text-4xl sm:text-5xl">
          {scopedWork ? `Ask about ${scopedWork.title}` : 'Ask the archive.'}
        </h1>
        <p className="mt-s4 max-w-xl leading-relaxed text-text2">
          {scopedWork
            ? 'Scoped reading: the guide retrieves from this work first, then widens to the rest of the archive.'
            : 'Retrieval-first answers from the corpus and the dossier — with sources, mode labels, and honest uncertainty.'}
        </p>
      </header>

      <GuidePanel
        workSlug={scopedWork?.slug ?? null}
        workTitle={scopedWork?.title ?? null}
        initialInput={q}
      />

      <p className="mt-s8 text-sm text-text3">
        The guide cites the{' '}
        <a href="/catalog" className="text-gold1 underline underline-offset-4 hover:text-gold2">
          proof-grounded catalog
        </a>{' '}
        when a question touches a formalized claim — browse it directly to see exactly
        what is proved, conditional, or open.
      </p>
    </div>
  );
}
