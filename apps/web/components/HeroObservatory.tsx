import Link from 'next/link';
import { OrbitalLines } from '@/components/OrbitalLines';

export function HeroObservatory({
  workCount,
  sectionCount,
}: {
  workCount: number;
  sectionCount: number;
}) {
  return (
    <section className="relative overflow-hidden pt-s16 pb-s12 sm:pt-s16">
      {/* orbital instrument */}
      <div className="pointer-events-none absolute -right-40 top-8 hidden h-[640px] w-[640px] opacity-70 lg:block">
        <OrbitalLines />
      </div>

      <div className="mx-auto max-w-archive px-s6">
        <p className="label animate-rise-in">A scholarly instrument · est. MMXXVI</p>

        <h1 className="serif-heading mt-s6 max-w-3xl animate-rise-in text-5xl sm:text-6xl lg:text-7xl">
          A living archive of{' '}
          <span className="text-gold1 italic">Leibniz</span>.
        </h1>

        <p className="mt-s6 max-w-2xl animate-rise-in text-lg leading-relaxed text-text2">
          Transcribed. Translated. Searchable. Guided.{' '}
          <span className="text-text1">
            Read Leibniz with sources, context, and an AI guide grounded in the
            texts themselves — never in invention.
          </span>
        </p>

        <div className="mt-s8 flex flex-wrap items-center gap-s4">
          <Link href="/works" className="btn-gold">
            Enter the archive
          </Link>
          <Link href="/guide" className="btn-ghost">
            Ask the guide <span aria-hidden="true">→</span>
          </Link>
        </div>

        <dl className="mt-s12 flex flex-wrap gap-x-s12 gap-y-s4">
          <div>
            <dt className="label">Works in the archive</dt>
            <dd className="serif-heading mt-1 text-3xl text-text1">{workCount}</dd>
          </div>
          <div>
            <dt className="label">Anchored sections</dt>
            <dd className="serif-heading mt-1 text-3xl text-text1">{sectionCount}</dd>
          </div>
          <div>
            <dt className="label">Evidence modes</dt>
            <dd className="serif-heading mt-1 text-3xl text-text1">4</dd>
          </div>
          <div>
            <dt className="label">Dossier layers</dt>
            <dd className="serif-heading mt-1 text-3xl text-text1">5</dd>
          </div>
        </dl>
      </div>
    </section>
  );
}
