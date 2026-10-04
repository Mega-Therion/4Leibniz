'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { WorkCard } from '@/components/WorkCard';
import { StatusBadge, ThemeBadge } from '@/components/ThemeBadge';
import type { ArchiveWork, WorkStatus } from '@/lib/types';

type ViewMode = 'cards' | 'list';

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: 'all', label: 'All statuses' },
  { value: 'translated', label: 'Translated' },
  { value: 'transcribed', label: 'Transcribed' },
  { value: 'completed', label: 'Completed' },
  { value: 'in-progress', label: 'In progress' },
];

function FilterSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="label">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="panel-flat min-w-40 px-s3 py-2 text-sm text-text1"
        style={{ background: 'var(--bg-1)' }}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export function ArchiveExplorer({
  works,
  themeLabels,
}: {
  works: ArchiveWork[];
  themeLabels: Map<string, string>;
}) {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('all');
  const [language, setLanguage] = useState('all');
  const [theme, setTheme] = useState('all');
  const [view, setView] = useState<ViewMode>('cards');

  const languages = useMemo(
    () => ['all', ...new Set(works.map((w) => w.language))],
    [works],
  );
  const themes = useMemo(
    () => ['all', ...new Set(works.flatMap((w) => w.themes))],
    [works],
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return works.filter((w) => {
      if (status !== 'all' && w.status !== status) return false;
      if (language !== 'all' && w.language !== language) return false;
      if (theme !== 'all' && !w.themes.includes(theme)) return false;
      if (q) {
        const haystack = `${w.title} ${w.altTitle ?? ''} ${w.summary}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [works, query, status, language, theme]);

  return (
    <div>
      {/* filter rail */}
      <div className="panel flex flex-col gap-s4 p-s4 sm:flex-row sm:items-end sm:flex-wrap lg:flex-nowrap">
        <label className="flex flex-1 flex-col gap-1">
          <span className="label">Search titles & abstracts</span>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. monad, substance, Arnauld…"
            className="panel-flat w-full px-s3 py-2 text-sm text-text1 placeholder:text-text3"
            style={{ background: 'var(--bg-1)' }}
            aria-label="Search the archive"
          />
        </label>

        <FilterSelect
          label="Status"
          value={status}
          onChange={setStatus}
          options={STATUS_OPTIONS}
        />
        <FilterSelect
          label="Language"
          value={language}
          onChange={setLanguage}
          options={languages.map((l) => ({
            value: l,
            label: l === 'all' ? 'All languages' : l.toUpperCase(),
          }))}
        />
        <FilterSelect
          label="Theme"
          value={theme}
          onChange={setTheme}
          options={themes.map((t) => ({
            value: t,
            label: t === 'all' ? 'All themes' : themeLabels.get(t) ?? t,
          }))}
        />

        <div
          className="flex gap-1 rounded-sm border border-line1 p-1"
          role="group"
          aria-label="View mode"
        >
          {(['cards', 'list'] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setView(mode)}
              aria-pressed={view === mode}
              className={`rounded-sm px-3 py-1.5 text-xs uppercase tracking-widest transition-colors ${
                view === mode ? 'bg-surface3 text-gold1' : 'text-text3 hover:text-text2'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      <p className="mt-s4 text-sm text-text3" role="status">
        {filtered.length} {filtered.length === 1 ? 'work' : 'works'}
        {filtered.length !== works.length && ` of ${works.length} in the archive`}
      </p>

      {/* results */}
      {filtered.length === 0 ? (
        <div className="panel mt-s6 p-s12 text-center">
          <p className="serif-heading text-2xl text-text1">Nothing found.</p>
          <p className="mt-s2 text-sm text-text3">
            No work matches those filters — try widening them, or{' '}
            <Link href="/guide" className="text-gold1 underline">
              ask the guide
            </Link>{' '}
            where a concept lives.
          </p>
        </div>
      ) : view === 'cards' ? (
        <div className="mt-s6 grid gap-s6 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((w) => (
            <WorkCard key={w.slug} work={w} themes={themeLabels} />
          ))}
        </div>
      ) : (
        <ul className="mt-s6 flex flex-col gap-2">
          {filtered.map((w) => (
            <li key={w.slug} className="border-b border-line1 pb-2 last:border-0">
              <Link
                href={`/works/${w.slug}`}
                className="group grid grid-cols-[1fr_auto] items-baseline gap-x-s6 gap-y-1 px-s2 py-s3 transition-colors hover:bg-surface3"
              >
                <div className="flex flex-wrap items-baseline gap-x-s3">
                  <span className="serif-heading text-xl text-text1 group-hover:text-gold1">
                    {w.title}
                  </span>
                  <span className="text-sm text-text3">{w.dateLabel}</span>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={w.status} />
                  <span className="label hidden sm:inline">
                    {w.sectionCount} §
                  </span>
                </div>
                <p className="col-span-full line-clamp-2 text-sm text-text3">
                  {w.summary}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
