/**
 * Read-only consumer of the 4Leibniz formal-claims catalog (contract v1).
 *
 * 4Leibniz is the canonical producer of `artifacts/v1/formal-claims.json`
 * (GitHub issue #11). This module consumes a packaged snapshot of that
 * artifact at `content/formal-claims-v1.json` — refreshed by copying the
 * artifact at a pinned commit. This app NEVER maintains an independent
 * theorem/proof-status catalog: `isFormallyVerified` is the only path by
 * which anything here can be labeled formally verified, and it returns true
 * only when the catalog entry's `status` is `proved`.
 */
import catalogJson from '@/content/formal-claims-v1.json';

export type FormalClaimStatus = 'proved' | 'conditional' | 'informal' | 'open_problem';

export interface FormalClaimSourceRef {
  type: 'file' | 'citation' | 'bridge' | 'machine';
  ref: string;
  line?: number;
}

export interface FormalClaimVerification {
  checked_by: string;
  toolchain: string;
  axioms: string[];
  sorries: number;
}

export interface FormalClaim {
  schema_version: string;
  claim_id: string;
  title: string;
  module: string;
  declaration: string;
  status: FormalClaimStatus;
  formal_statement?: string;
  conditional_on?: string[];
  proof_source: { repository: string; commit: string; path: string };
  source_refs: FormalClaimSourceRef[];
  verification?: FormalClaimVerification;
  human_summary: string;
}

export interface FormalClaimsCatalog {
  schema_version: string;
  generator: { name: string; version: string };
  generated_at: string;
  source: { repository: string; commit: string; lean_toolchain: string };
  verification_record: {
    lean_available: boolean;
    lake_build_exit_code: number | null;
    sorries: number;
    notes: string;
  };
  claims: FormalClaim[];
}

export const CATALOG_SCHEMA_VERSION = 'v1';

export interface CatalogView {
  catalog: FormalClaimsCatalog;
  listClaims(): readonly FormalClaim[];
  getClaim(claimId: string): FormalClaim | undefined;
  /** True only when the catalog entry's status is `proved`. */
  isFormallyVerified(claimId: string): boolean;
  describeClaim(claimId: string): ClaimDisplay | null;
  matchClaimsInText(text: string): FormalClaim[];
}

/**
 * Build a read-only view over a catalog. `isFormallyVerified` on the returned
 * view is the ONLY path by which anything in this app can label a claim
 * formally verified — and it returns true only for catalog entries whose
 * `status` is `proved` (grounded by the pinned Lean toolchain in 4Leibniz).
 */
export function createCatalogView(cat: FormalClaimsCatalog): CatalogView {
  const byId = new Map<string, FormalClaim>(cat.claims.map((c) => [c.claim_id, c]));
  const view: CatalogView = {
    catalog: cat,
    listClaims: () => cat.claims,
    getClaim: (claimId) => byId.get(claimId),
    isFormallyVerified: (claimId) => byId.get(claimId)?.status === 'proved',
    describeClaim: (claimId) => describeClaimFrom(byId, claimId),
    matchClaimsInText: (text) => matchClaimsFrom(cat.claims, text),
  };
  return view;
}

function describeClaimFrom(
  byId: Map<string, FormalClaim>,
  claimId: string,
): ClaimDisplay | null {
  const claim = byId.get(claimId);
  if (!claim) return null;
  return {
    claim_id: claim.claim_id,
    title: claim.title,
    module: claim.module,
    status: claim.status,
    status_label: statusLabel(claim.status),
    sourced_explanation: claim.human_summary,
    verified_provenance:
      claim.status === 'proved' && claim.verification
        ? {
            repository: claim.proof_source.repository,
            commit: claim.proof_source.commit,
            path: claim.proof_source.path,
            declaration: claim.declaration,
            toolchain: claim.verification.toolchain,
            axioms: claim.verification.axioms,
          }
        : null,
    ...(claim.conditional_on ? { conditional_on: claim.conditional_on } : {}),
  };
}

function matchClaimsFrom(claims: FormalClaim[], text: string): FormalClaim[] {
  const lower = text.toLowerCase();
  const matches: FormalClaim[] = [];
  for (const claim of claims) {
    const short = claim.declaration.split('.').pop() ?? claim.declaration;
    if (
      lower.includes(claim.claim_id.toLowerCase()) ||
      (short.length >= 4 && lower.includes(short.toLowerCase()))
    ) {
      matches.push(claim);
    }
  }
  return matches;
}

/** The packaged snapshot. Read-only: never mutated at runtime. */
export const catalog: FormalClaimsCatalog = catalogJson as FormalClaimsCatalog;

/** Default view over the packaged snapshot. */
export const formalClaims: CatalogView = createCatalogView(catalog);

export function listClaims(): readonly FormalClaim[] {
  return formalClaims.listClaims();
}

export function getClaim(claimId: string): FormalClaim | undefined {
  return formalClaims.getClaim(claimId);
}

/**
 * THE verification gate for this app. True only when the catalog — produced
 * by the pinned Lean toolchain through 4Leibniz — marks the claim `proved`.
 * No other code path may label anything formally verified.
 */
export function isFormallyVerified(claimId: string): boolean {
  return formalClaims.isFormallyVerified(claimId);
}

/** Human-facing label for a claim status. */
export function statusLabel(status: FormalClaimStatus): string {
  switch (status) {
    case 'proved':
      return 'Formally verified (Lean)';
    case 'conditional':
      return 'Conditional on recorded assumptions';
    case 'informal':
      return 'Informal (not formalized)';
    case 'open_problem':
      return 'Open problem';
  }
}

export interface ClaimDisplay {
  claim_id: string;
  title: string;
  module: string;
  status: FormalClaimStatus;
  status_label: string;
  /** Sourced explanation — human-readable, never a verification claim. */
  sourced_explanation: string;
  /** Formal proof provenance. Present ONLY for proved claims. */
  verified_provenance:
    | {
        repository: string;
        commit: string;
        path: string;
        declaration: string;
        toolchain: string;
        axioms: string[];
      }
    | null;
  /** Assumptions, for conditional claims. */
  conditional_on?: string[];
}
