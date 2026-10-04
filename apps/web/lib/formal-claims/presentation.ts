/**
 * Presentation layer for the proof-grounded catalog (v1.1 UI surfacing).
 *
 * Pure, catalog-agnostic helpers: they group and count claims but never
 * re-derive status. The only source of truth for "proved" is the catalog
 * entry's `status` field (see `isFormallyVerified` in ./index).
 */
import type { FormalClaim, FormalClaimStatus } from './index';

export interface ModuleGroup<T = FormalClaim> {
  module: string;
  claims: T[];
}

export interface CatalogStats {
  total: number;
  proved: number;
  conditional: number;
  informal: number;
  open_problem: number;
}

/** Group claims by module, modules in catalog order of first appearance. */
export function groupByModule<T extends { module: string }>(claims: readonly T[]): ModuleGroup<T>[] {
  const groups: ModuleGroup<T>[] = [];
  const index = new Map<string, ModuleGroup<T>>();
  for (const claim of claims) {
    let group = index.get(claim.module);
    if (!group) {
      group = { module: claim.module, claims: [] };
      index.set(claim.module, group);
      groups.push(group);
    }
    group.claims.push(claim);
  }
  return groups;
}

/** Counts by status. Totals always equal the input length. */
export function catalogStats(claims: readonly FormalClaim[]): CatalogStats {
  const stats: CatalogStats = {
    total: claims.length,
    proved: 0,
    conditional: 0,
    informal: 0,
    open_problem: 0,
  };
  for (const claim of claims) stats[claim.status]++;
  return stats;
}

/** Chip variant for a claim status — honest colors, no status inflation. */
export function statusChipVariant(status: FormalClaimStatus): 'gold' | 'violet' | 'plain' {
  switch (status) {
    case 'proved':
      return 'gold';
    case 'conditional':
      return 'violet';
    case 'open_problem':
      return 'violet';
    case 'informal':
      return 'plain';
  }
}

/** Per-claim display model for the catalog page. `verified_provenance` is
 * non-null ONLY for proved claims — the page renders it as proof evidence,
 * everything else as sourced explanation. */
export interface ClaimCardModel {
  claim_id: string;
  title: string;
  module: string;
  declaration: string;
  status: FormalClaimStatus;
  status_label: string;
  chip_variant: 'gold' | 'violet' | 'plain';
  human_summary: string;
  conditional_on: string[];
  verified_provenance: {
    repository: string;
    commit: string;
    path: string;
    toolchain: string;
    axioms: string[];
  } | null;
}

export function toClaimCardModel(
  claim: FormalClaim,
  statusLabel: (s: FormalClaimStatus) => string,
): ClaimCardModel {
  return {
    claim_id: claim.claim_id,
    title: claim.title,
    module: claim.module,
    declaration: claim.declaration,
    status: claim.status,
    status_label: statusLabel(claim.status),
    chip_variant: statusChipVariant(claim.status),
    human_summary: claim.human_summary,
    conditional_on: claim.conditional_on ?? [],
    verified_provenance:
      claim.status === 'proved' && claim.verification
        ? {
            repository: claim.proof_source.repository,
            commit: claim.proof_source.commit,
            path: claim.proof_source.path,
            toolchain: claim.verification.toolchain,
            axioms: claim.verification.axioms,
          }
        : null,
  };
}
