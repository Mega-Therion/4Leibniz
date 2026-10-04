import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="mx-auto flex max-w-archive flex-col items-center px-s6 py-s16 text-center">
      <p className="label">Error · 404</p>
      <h1 className="serif-heading mt-s4 text-5xl text-text1">
        This shelf is empty.
      </h1>
      <p className="mt-s4 max-w-md text-text2">
        The page you asked for is not in the archive. The collection is young —
        but the reader is exacting.
      </p>
      <div className="mt-s8 flex flex-wrap justify-center gap-s4">
        <Link href="/works" className="btn-gold">
          Explore the archive
        </Link>
        <Link href="/guide" className="btn-ghost">
          Ask the guide
        </Link>
      </div>
    </div>
  );
}
