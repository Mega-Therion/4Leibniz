import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ReaderSectionNav } from '@/components/ReaderSectionNav';
import { ReaderContent } from '@/components/ReaderContent';
import { WorkMetadataPanel } from '@/components/WorkMetadataPanel';
import { getWork, getWorks, getThemes, getConcepts } from '@/lib/content';
import type { Concept } from '@/lib/types';

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const works = await getWorks();
  return works.map((w) => ({ slug: w.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const work = await getWork(slug);
  if (!work) return { title: 'Work not found' };
  const title = work.title;
  const description = work.summary.slice(0, 180);
  return {
    title,
    description,
    alternates: { canonical: `/works/${work.slug}` },
    openGraph: {
      title: `${title} — 4Leibniz`,
      description,
      url: `/works/${work.slug}`,
    },
  };
}

export default async function WorkPage({ params }: PageProps) {
  const { slug } = await params;
  const work = await getWork(slug);
  if (!work) notFound();

  const [themes, concepts, allWorks] = await Promise.all([
    getThemes(),
    getConcepts(),
    getWorks(),
  ]);
  const themeLabels = new Map(
    (themes as { slug: string; label: string }[]).map((t) => [t.slug, t.label]),
  );
  const conceptList = concepts as Concept[];
  const relatedConcepts = work.relatedConcepts
    .map((slug) => conceptList.find((c) => c.slug === slug))
    .filter((c): c is Concept => Boolean(c))
    .map((c) => ({ slug: c.slug, term: c.term }));
  const relatedWorks = allWorks
    .filter(
      (w) =>
        w.slug !== work.slug && w.themes.some((t) => work.themes.includes(t)),
    )
    .map((w) => ({ slug: w.slug, title: w.title }));

  return (
    <div className="mx-auto max-w-archive px-s6 pt-s12">
      {/* work header */}
      <header className="border-b border-line1 pb-s8">
        <p className="label">
          <Link href="/works" className="text-text3 hover:text-gold1">
            Archive
          </Link>{' '}
          / {work.dateLabel}
        </p>
        <h1 className="serif-heading mt-s3 max-w-3xl text-4xl sm:text-5xl">
          {work.title}
        </h1>
        {work.altTitle && (
          <p className="mt-s3 text-lg italic text-text3">{work.altTitle}</p>
        )}
        <p className="mt-s4 max-w-2xl leading-relaxed text-text2">{work.summary}</p>
      </header>

      {/* reader grid */}
      <div className="grid gap-s12 py-s12 lg:grid-cols-[220px_minmax(0,1fr)_320px]">
        <div className="hidden lg:block">
          <ReaderSectionNav sections={work.sections} workSlug={work.slug} />
        </div>

        <div className="min-w-0">
          <ReaderContent work={work} />
          <nav
            aria-label="Sections mobile"
            className="mt-s8 border-t border-line1 pt-s6 lg:hidden"
          >
            <ReaderSectionNav sections={work.sections} workSlug={work.slug} />
          </nav>
        </div>

        <WorkMetadataPanel
          work={work}
          themeLabels={themeLabels}
          relatedWorks={relatedWorks}
          relatedConcepts={relatedConcepts}
        />
      </div>
    </div>
  );
}
