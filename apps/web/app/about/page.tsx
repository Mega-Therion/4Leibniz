import type { Metadata } from 'next';
import { SectionFrame } from '@/components/SectionFrame';
import { OrbitalLines } from '@/components/OrbitalLines';

export const metadata: Metadata = {
  title: 'About & Method',
  description:
    'What 4Leibniz is, how its editions are made, how the AI guide stays grounded, and where the archive goes next.',
  alternates: { canonical: '/about' },
};

export default function AboutPage() {
  return (
    <>
      <SectionFrame
        eyebrow="About"
        title="A digital monument, built like an instrument."
        description="4Leibniz is a public scholarly archive and AI-guided reading environment for the works of Leibniz. It is not a chatbot wrapped in branding: the guide answers from retrieved evidence, the archive is citation-aware down to the section anchor, and the editorial method is on display."
        className="pt-s12"
      >
        <div className="grid gap-s6 lg:grid-cols-3">
          {[
            {
              k: 'The archive',
              v: 'Works are transcribed, translated, and structured into anchored sections. Each edition records its provenance — what text was used and what remains provisional. Anchors are permanent: citations survive edition upgrades.',
            },
            {
              k: 'The dossier',
              v: 'Biography, timeline, concepts, correspondents, and themes live in a structured editorial layer — the background the guide may use, but always labeled as editorial, never as Leibniz.',
            },
            {
              k: 'The guide',
              v: 'Retrieval-first. Questions are embedded and matched against the corpus (pgvector), the answer streams with a mode badge and a citations drawer, and insufficient evidence is reported as insufficient. Never an invented quotation.',
            },
          ].map((item) => (
            <div key={item.k} className="panel p-s6">
              <h3 className="serif-heading text-xl text-gold1">{item.k}</h3>
              <p className="mt-s3 text-sm leading-relaxed text-text2">{item.v}</p>
            </div>
          ))}
        </div>
      </SectionFrame>

      <SectionFrame
        eyebrow="Editorial method"
        title="How the editions are made."
        className="mt-s16"
      >
        <div className="mx-auto max-w-2xl space-y-6 text-sm leading-[1.9] text-text2">
          <p>
            The current seed editions begin from public-domain translations of
            record — Montgomery (1908) for the Discourse on Metaphysics, Latta
            (1898) for the Monadology — digitized on Wikisource and lightly
            proofed. The provenance of every text is stated on its work page.
          </p>
          <p>
            As the archive's own transcriptions and re-translations are
            completed, they replace the seed texts in place. Section anchors are
            stable across that transition, so every citation — inside the
            archive, from the guide, or from the wider web — keeps resolving.
          </p>
          <p>
            The corpus is indexed by section-aware chunking: each chunk carries
            its work, section, and anchor, so retrieved evidence always points
            to a place a reader can open and check. French and Latin originals
            are the next milestone for side-by-side reading.
          </p>
        </div>
      </SectionFrame>

      <SectionFrame
        eyebrow="Licensing"
        title="Public texts, honest citations."
        className="mt-s16"
      >
        <div className="mx-auto max-w-2xl space-y-6 text-sm leading-[1.9] text-text2">
          <p>
            Leibniz's texts, and the seed translations used here, are in the
            public domain. Editorial introductions, dossier entries, and the
            site itself are © 2026 4Leibniz.
          </p>
          <p>
            The AI guide is a reading instrument, not an authority. Its answers
            are grounded in retrieved sources but can be wrong. Open the
            citations; read the passages; verify.
          </p>
        </div>
      </SectionFrame>

      <section className="relative mt-s16 overflow-hidden py-s12 text-center">
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-80 w-80 -translate-x-1/2 -translate-y-1/2 opacity-25">
          <OrbitalLines />
        </div>
        <p className="relative serif-heading text-3xl text-text1">
          Calculemus.
        </p>
      </section>
    </>
  );
}
