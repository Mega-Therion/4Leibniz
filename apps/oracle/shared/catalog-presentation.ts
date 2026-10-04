/**
 * Presentation helpers for the formal-claims catalog UI (v1.1 surfacing).
 *
 * Pure grouping/counting only — the source of truth for a claim's status is
 * always the packaged catalog (shared/formal-claims). `formally_verified`
 * means exactly "catalog status === proved", nothing else.
 */
import type { FormalClaim } from "./formal-claims.js";

export interface ModuleGroup<T = FormalClaim> {
  module: string;
  claims: T[];
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

export interface CatalogStats {
  total: number;
  proved: number;
  conditional: number;
  informal: number;
  open_problem: number;
}

/** Counts by status; total always equals input length. */
export function catalogStats(claims: readonly FormalClaim[]): CatalogStats {
  const stats: CatalogStats = { total: claims.length, proved: 0, conditional: 0, informal: 0, open_problem: 0 };
  for (const claim of claims) stats[claim.status]++;
  return stats;
}

/** A lighter row model for the catalog list UI. */
export interface ClaimRow {
  claim_id: string;
  title: string;
  module: string;
  status: FormalClaim["status"];
  status_label: string;
  formally_verified: boolean;
  human_summary: string;
}

export function toClaimRow(claim: FormalClaim, statusLabelFn: (s: FormalClaim["status"]) => string): ClaimRow {
  return {
    claim_id: claim.claim_id,
    title: claim.title,
    module: claim.module,
    status: claim.status,
    status_label: statusLabelFn(claim.status),
    formally_verified: claim.status === "proved",
    human_summary: claim.human_summary,
  };
}

/** Status filter for the catalog screen. */
export type StatusFilter = "all" | "proved" | "conditional" | "informal" | "open_problem";

export function matchesFilter(claim: { status: string }, filter: StatusFilter): boolean {
  return filter === "all" || claim.status === filter;
}
