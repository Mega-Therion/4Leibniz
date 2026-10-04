import type { Metadata } from 'next';
import Link from 'next/link';
import { SectionFrame } from '@/components/SectionFrame';
import { getBiography, getThemes, getWorks, getConcepts } from '@/lib/content';

export const metadata: Metadata = {
  title: 'The Leibniz Dossier',
  description:
    'A structured dossier of Leibniz: biography, timeline, concepts, correspondents, and themes — the editorial background layer behind the archive.',
  alternates: { canonical: '/leibniz' },
};

export default async function LeibnizPage() {
  const [bio, themes, works, concepts] = await Promise.all([
    getBiography(),
    getThemes(),
    getWorks(),
    getConcepts(),
  ]);

  const workTitles = new Map(works.map((w) => [w.slug, w.title]));

  return (
    <>
      <SectionFrame
        eyebrow="The dossier"
        title="Leibniz, in layers."
        description="The dossier is the archive's editorial background: biography, timeline, concepts, correspondents, and themes — curated, structured, and clearly labeled so the guide never passes it off as Leibniz's own words."
        className="pt-s12"
      >
        <div className="grid gap-6 lg:grid-cols-4">
          {[
            { href: '/leibniz/timeline', label: 'Timeline', desc: '1646–1765, the whole arc' },
            { href: '/leibniz/concepts', label: 'Concepts', desc: `${(concepts as unknown[]).length} glossary entries` },
            { href: '/leibniz/correspondents', label: 'Correspondents', desc: 'The letter network' },
            { href: '/works', label: 'The texts', desc: 'The archive itself' },
          ].map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className="panel group p-s6 transition-transform hover:-translate-y-1"
            >
              <p className="serif-heading text-2xl text-text1 group-hover:text-gold1">
                {card.label}
              </p>
              <p className="mt-s2 text-sm text-text3">{card.desc}</p>
            </Link>
          ))}
        </div>
      </SectionFrame>

      <SectionFrame
        eyebrow="Biography"
        title="The last universal mind."
        className="mt-s16"
      >
        <article className="reader-prose max-w-2xl">
          {bio.map((paragraph, i) => (
            <p key={i}>{paragraph}</p>
          ))}
        </article>
      </SectionFrame>

      <SectionFrame
        eyebrow="Themes & works"
        title="The relation map."
        description="Every work is filed under themes; every theme points back to its texts. This is the same map the guide uses to route questions."
        className="mt-s16"
      >
        <div className="grid gap-s6 sm:grid-cols-2 xl:grid-cols-4">
          {(themes as { slug: string; label: string; description: string; works: string[] }[]).map(
            (theme) => (
              <div key={theme.slug} className="panel p-s6">
                <h3 className="serif-heading text-xl text-gold1">{theme.label}</h3>
                <p className="mt-s3 text-sm leading-relaxed text-text2">
                  {theme.description}
                </p>
                <ul className="mt-s4 flex flex-col gap-2 border-t border-line1 pt-s4 text-sm">
                  {theme.works.map((slug) => (
                    <li key={slug}>
                      <Link
                        href={`/works/${slug}`}
                        className="text-text2 underline decoration-gold2 underline-offset-4 hover:text-gold1"
                      >
                        {workTitles.get(slug) ?? slug}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ),
          )}
        </div>
      </SectionFrame>
    </>
  );
}
