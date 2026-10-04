import Link from 'next/link';
import { HeroObservatory } from '@/components/HeroObservatory';
import { SectionFrame } from '@/components/SectionFrame';
import { WorkCard } from '@/components/WorkCard';
import { ModeBadge } from '@/components/GuideMessage';
import { OrbitalLines } from '@/components/OrbitalLines';
import { getWorks, getThemes, getTimeline } from '@/lib/content';
import type { ArchiveWork } from '@/lib/types';

export default async function HomePage() {
  const [works, themes, timeline] = await Promise.all([getWorks(), getThemes(), getTimeline()]);
  const themeLabels = new Map((themes as { slug: string; label: string }[]).map((t) => [t.slug, t.label]));
  const sectionCount = works.reduce((acc, w) => acc + w.sections.length, 0);
  const featured = works.filter((w) => w.featured);
  const milestones = (timeline as { dateLabel: string; title: string; slug: string }[]).slice(0, 4);

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
    <>
      <HeroObservatory workCount={works.length} sectionCount={sectionCount} />

      {/* mission */}
      <SectionFrame
        id="mission"
        eyebrow="The mission"
        title="Read Leibniz the way he deserves to be read."
        description="4Leibniz is a public scholarly archive of Leibniz's works — transcribed, translated, and anchored to stable citations — with an AI guide that answers from the texts, shows its evidence, and admits what it does not know. No invented quotations. No fabricated dates. Sources first."
        className="pt-s12"
      >
        <figure className="panel mx-auto max-w-2xl p-s8">
          <blockquote className="serif-heading text-2xl italic leading-relaxed text-text1">
            “The general knowledge of this great truth, that God acts always in
            the most perfect and most desirable manner possible, is in my
            opinion the basis of the love which we owe to God in all things.”
          </blockquote>
          <figcaption className="mt-s4 text-sm text-text3">
            <Link
              href="/works/discourse-on-metaphysics#iv"
              className="text-gold2 underline decoration-gold2 underline-offset-4 hover:text-gold1"
            >
              Discourse on Metaphysics §IV
            </Link>{' '}
            — Montgomery translation, 1908
          </figcaption>
        </figure>
      </SectionFrame>

      {/* featured works */}
      <SectionFrame
        id="featured"
        eyebrow="The archive"
        title="Featured editions"
        description="Every work is sectioned, anchored, and indexed for retrieval. Begin with the two pillars of the mature system."
        className="mt-s16"
      >
        <div className="grid gap-s6 sm:grid-cols-2 lg:grid-cols-3">
          {featured.map((w) => (
            <WorkCard key={w.slug} work={w as unknown as ArchiveWork} themes={themeLabels} />
          ))}
        </div>
        <div className="mt-s8">
          <Link href="/works" className="btn-ghost">
            Browse all {works.length} works <span aria-hidden="true">→</span>
          </Link>
        </div>
      </SectionFrame>

      {/* guide explainer */}
      <SectionFrame
        id="guide"
        eyebrow="The guide"
        title="An AI that shows its receipts."
        description="The 4Leibniz Guide is retrieval-first. Every question triggers a semantic search through the corpus and the editorial dossier; the answer is composed from what was actually retrieved, and each source is cited with a link you can open and check."
        className="mt-s16"
      >
        <div className="grid gap-s6 lg:grid-cols-2">
          <div className="panel relative overflow-hidden p-s6">
            <div className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 opacity-40">
              <OrbitalLines />
            </div>
            <p className="label">How it answers</p>
            <ul className="mt-s4 flex flex-col gap-s3 text-sm leading-relaxed text-text2">
              <li className="flex gap-s3">
                <span className="text-gold1">01</span> Your question is embedded and matched
                against every anchored section of the corpus.
              </li>
              <li className="flex gap-s3">
                <span className="text-gold1">02</span> The editorial dossier is probed for
                biography, concepts, and correspondents — labeled as background, never as text.
              </li>
              <li className="flex gap-s3">
                <span className="text-gold1">03</span> The answer streams with a mode badge
                and a citations drawer. Insufficient evidence is called out, not papered over.
              </li>
            </ul>
          </div>
          <div className="panel p-s6">
            <p className="label">Evidence modes</p>
            <ul className="mt-s4 flex flex-col gap-s4 text-sm text-text2">
              <li className="flex items-center gap-s3">
                <ModeBadge mode="corpus" /> grounded in archive texts
              </li>
              <li className="flex items-center gap-s3">
                <ModeBadge mode="dossier" /> grounded in editorial background
              </li>
              <li className="flex items-center gap-s3">
                <ModeBadge mode="mixed" /> texts plus background
              </li>
              <li className="flex items-center gap-s3">
                <ModeBadge mode="insufficient_evidence" /> the guide says so plainly
              </li>
            </ul>
            <div className="mt-s6">
              <Link href="/guide" className="btn-gold">
                Enter the guide
              </Link>
            </div>
          </div>
        </div>
      </SectionFrame>

      {/* Leibniz intro */}
      <SectionFrame
        id="leibniz"
        eyebrow="The thinker"
        title="The last man who knew everything is an understatement."
        description="Mathematician, metaphysician, diplomat, jurist, historian, mining engineer, librarian, logician — Leibniz invented the calculus and the binary arithmetic at the bottom of this very website, and imagined a language in which reasoning could be computed. This archive is devoted to his texts, read closely."
        className="mt-s16"
      >
        <div className="grid gap-s6 lg:grid-cols-3">
          {milestones.map((m, i) => (
            <Link
              key={m.slug}
              href="/leibniz/timeline"
              className="panel group p-s6 transition-transform hover:-translate-y-1"
            >
              <p className="font-mono text-sm text-gold2">
                {String(i + 1).padStart(2, '0')} · {m.dateLabel}
              </p>
              <p className="serif-heading mt-s2 text-xl text-text1 group-hover:text-gold1">
                {m.title}
              </p>
            </Link>
          ))}
          <Link href="/leibniz" className="btn-ghost h-fit justify-self-start">
            Meet Leibniz — the dossier <span aria-hidden="true">→</span>
          </Link>
        </div>
      </SectionFrame>

      {/* editorial care */}
      <SectionFrame
        id="method"
        eyebrow="The method"
        title="Editorial care is a feature, not a footnote."
        description="Each edition records its provenance: what text was used, what was corrected, what remains provisional. Seed editions begin from public-domain translations; as the archive's own transcriptions and re-translations are completed, they replace the seed texts — same anchors, new evidence."
        className="mt-s16"
      >
        <div className="grid gap-s6 sm:grid-cols-3">
          {[
            {
              k: 'Transcription',
              v: 'Source scans aligned, extracted, and proofed. Section anchors are permanent — they survive edition changes.',
            },
            {
              k: 'Translation',
              v: 'Public-domain translations seed each work; the archive re-translates deliberately, with the translator credited on every page.',
            },
            {
              k: 'Retrieval',
              v: 'Texts are chunked by section, embedded, and indexed with pgvector. The guide can only cite what actually exists.',
            },
          ].map((item) => (
            <div key={item.k} className="panel p-s6">
              <p className="serif-heading text-xl text-gold1">{item.k}</p>
              <p className="mt-s3 text-sm leading-relaxed text-text2">{item.v}</p>
            </div>
          ))}
        </div>
      </SectionFrame>

      {/* final CTA */}
      <section className="mt-s16 overflow-hidden py-s16 text-center">
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-[520px] w-[520px] -translate-x-1/2 -translate-y-1/2 opacity-30">
          <OrbitalLines />
        </div>
        <div className="relative mx-auto max-w-archive px-s6">
          <p className="label">Calculemus — let us calculate</p>
          <h2 className="serif-heading mt-s4 text-4xl sm:text-5xl">
            The archive is open.
          </h2>
          <p className="mx-auto mt-s4 max-w-xl text-text2">
            {works.length} works, {sectionCount} anchored sections, one guide
            that answers with evidence. Start reading, or start asking.
          </p>
          <div className="mt-s8 flex flex-wrap justify-center gap-s4">
            <Link href="/works" className="btn-gold">
              Explore the archive
            </Link>
            <Link href="/guide" className="btn-ghost">
              Enter the guide
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
