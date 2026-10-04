import Link from 'next/link';

export function SiteFooter() {
  return (
    <footer className="relative mt-s16 border-t border-line1">
      <div className="gold-rule mx-auto max-w-archive" />
      <div className="mx-auto grid max-w-archive gap-s8 px-s6 py-s12 sm:grid-cols-2 lg:grid-cols-4">
        <div className="sm:col-span-2">
          <p className="serif-heading text-xl text-text1">4Leibniz</p>
          <p className="mt-s3 max-w-sm text-sm leading-relaxed text-text3">
            A living archive of Leibniz — transcribed, translated, searchable,
            guided. Built as a public scholarly instrument.
          </p>
        </div>
        <nav aria-label="Archive">
          <p className="label mb-s3">Archive</p>
          <ul className="space-y-2 text-sm">
            <li>
              <Link href="/works" className="text-text2 hover:text-gold1">
                All works
              </Link>
            </li>
            <li>
              <Link
                href="/works/discourse-on-metaphysics"
                className="text-text2 hover:text-gold1"
              >
                Discourse on Metaphysics
              </Link>
            </li>
            <li>
              <Link href="/works/monadology" className="text-text2 hover:text-gold1">
                The Monadology
              </Link>
            </li>
          </ul>
        </nav>
        <nav aria-label="Study">
          <p className="label mb-s3">Study</p>
          <ul className="space-y-2 text-sm">
            <li>
              <Link href="/guide" className="text-text2 hover:text-gold1">
                AI Guide
              </Link>
            </li>
            <li>
              <Link href="/leibniz/timeline" className="text-text2 hover:text-gold1">
                Timeline
              </Link>
            </li>
            <li>
              <Link href="/leibniz/concepts" className="text-text2 hover:text-gold1">
                Concepts
              </Link>
            </li>
            <li>
              <Link href="/about" className="text-text2 hover:text-gold1">
                About & Method
              </Link>
            </li>
          </ul>
        </nav>
      </div>
      <div className="border-t border-line1 px-s6 py-s4">
        <p className="mx-auto max-w-archive text-xs leading-relaxed text-text3">
          © 2026 4Leibniz. Texts are public-domain editions, cited per work. AI
          answers are retrieval-grounded but can be wrong — verify against the
          cited sections. <span className="text-gold2">Calculemus.</span>
        </p>
      </div>
    </footer>
  );
}
