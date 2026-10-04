'use client';

import { useMemo, useState } from 'react';
import { ThemeBadge } from '@/components/ThemeBadge';
import type { ClaimCardModel, ModuleGroup } from '@/lib/formal-claims/presentation';

type StatusFilter = 'all' | 'proved' | 'conditional' | 'informal' | 'open_problem';

const FILTERS: { key: StatusFilter; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'proved', label: 'Formally verified' },
  { key: 'conditional', label: 'Conditional' },
  { key: 'informal', label: 'Informal' },
  { key: 'open_problem', label: 'Open problems' },
];

/**
 * The proof-grounded catalog listing. Status labels come from the catalog
 * itself; verified provenance is rendered only for proved claims.
 */
export function ClaimCatalog({ groups }: { groups: ModuleGroup<ClaimCardModel>[] }) {
  const [filter, setFilter] = useState<StatusFilter>('all');

  const visible = useMemo(() => {
    if (filter === 'all') return groups;
    return groups
      .map((g) => ({
        module: g.module,
        claims: g.claims.filter((c) => c.status === filter),
      }))
      .filter((g) => g.claims.length > 0);
  }, [groups, filter]);

  const shown = visible.reduce((n, g) => n + g.claims.length, 0);
  const total = groups.reduce((n, g) => n + g.claims.length, 0);

  return (
    <div>
      <div className="mt-s6 flex flex-wrap items-center gap-s2">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            type="button"
            onClick={() => setFilter(f.key)}
            aria-pressed={filter === f.key}
            className={`chip cursor-pointer transition-colors ${
              filter === f.key ? 'chip-gold' : ''
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <p className="mt-s4 text-sm text-text3" role="status">
        {shown} of {total} catalogued claims
      </p>

      {visible.map((group) => (
        <section key={group.module} className="mt-s10">
          <div className="flex items-baseline gap-s3">
            <h2 className="serif-heading text-2xl text-text1">{group.module}</h2>
          </div>
          <div className="gold-rule mt-s3 w-12" />

          <div className="mt-s6 grid gap-s5">
            {group.claims.map((claim) => (
              <article
                key={claim.claim_id}
                id={claim.claim_id}
                className="panel flex scroll-mt-28 flex-col gap-s3 p-s6"
              >
                <div className="flex flex-wrap items-start justify-between gap-s3">
                  <h3 className="serif-heading text-xl text-text1">{claim.title}</h3>
                  <ThemeBadge
                    label={claim.status_label}
                    variant={claim.chip_variant}
                  />
                </div>

                <p className="font-mono text-xs leading-relaxed text-text3">
                  {claim.declaration}
                </p>

                <p className="text-sm leading-relaxed text-text2">{claim.human_summary}</p>

                {claim.conditional_on.length > 0 && (
                  <div className="text-sm text-text2">
                    <p className="label">Conditional on</p>
                    <ul className="mt-s2 list-disc space-y-1 pl-5 font-mono text-xs text-text3">
                      {claim.conditional_on.map((dep) => (
                        <li key={dep}>{dep}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {claim.verified_provenance && (
                  <div className="mt-s1 rounded-md border border-line2 bg-bg1 p-s4 text-xs leading-relaxed text-text3">
                    <p className="label">Proof provenance</p>
                    <p className="mt-s2">
                      Checked by the pinned Lean toolchain ({claim.verified_provenance.toolchain})
                      in {claim.verified_provenance.repository} at commit{' '}
                      <span className="font-mono">
                        {claim.verified_provenance.commit.slice(0, 12)}
                      </span>
                      , {claim.verified_provenance.path}. Standard axioms only:{' '}
                      {claim.verified_provenance.axioms.join(', ')}. Zero sorry.
                    </p>
                  </div>
                )}
              </article>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
