interface ReaderSectionNavProps {
  sections: { label: string; title: string | null; anchor: string }[];
  workSlug: string;
}

/** Sticky subsection rail — every heading is a stable anchor. */
export function ReaderSectionNav({ sections, workSlug }: ReaderSectionNavProps) {
  return (
    <nav aria-label="Sections" className="sticky top-28">
      <p className="label">Sections</p>
      <div className="gold-rule mt-s3 w-12" />
      <ol className="mt-s4 flex max-h-[60vh] flex-col gap-1 overflow-y-auto pr-2 text-sm">
        {sections.map((s) => (
          <li key={s.anchor}>
            <a
              href={`#${s.anchor}`}
              className="group flex items-baseline gap-2 rounded-sm px-2 py-1.5 text-text3 transition-colors hover:bg-surface3 hover:text-text1"
            >
              <span className="font-mono text-xs text-gold2 group-hover:text-gold1">
                {s.label}
              </span>
              <span className="line-clamp-1">{s.title ?? `Section ${s.label}`}</span>
            </a>
          </li>
        ))}
      </ol>
      <p className="mt-s4 border-t border-line1 pt-s4 text-xs text-text3">
        {sections.length} anchored sections · <code className="text-gold2">/works/{workSlug}#§</code>
      </p>
    </nav>
  );
}
