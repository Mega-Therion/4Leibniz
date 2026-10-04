/**
 * Contract tests for the formal-claims consumer (4Leibniz issue #11).
 *
 * The Oracle is a consumer, never a producer: it may explain a catalogued
 * claim but can label something formally verified ONLY through
 * `isFormallyVerified`, which is true only for catalog `proved` entries.
 */
import { describe, expect, it } from "vitest";
import {
  catalog,
  createCatalogView,
  CATALOG_SCHEMA_VERSION,
  formalClaims,
  statusLabel,
  type FormalClaim,
  type FormalClaimsCatalog,
} from "../shared/formal-claims";
import { appRouter } from "../server/routers";
import { catalogStats, groupByModule, toClaimRow, matchesFilter } from "../shared/catalog-presentation";
import fixtureJson from "./fixtures/formal-claims/formal-claims-v1.fixture.json";

const STATUSES = ["proved", "conditional", "informal", "open_problem"] as const;
const STANDARD_AXIOMS = new Set(["propext", "Classical.choice", "Quot.sound"]);
const COMMIT_RE = /^[0-9a-f]{40}$/;

function catalogInvariants(cat: FormalClaimsCatalog) {
  expect(cat.schema_version).toBe(CATALOG_SCHEMA_VERSION);
  expect(cat.source.repository).toBe("Mega-Therion/4Leibniz");
  expect(cat.source.commit).toMatch(COMMIT_RE);
  const ids = cat.claims.map((c) => c.claim_id);
  expect([...ids].sort()).toEqual(ids);
  expect(new Set(ids).size).toBe(ids.length);
  for (const claim of cat.claims) {
    expect(STATUSES).toContain(claim.status);
    expect(claim.source_refs.length).toBeGreaterThan(0);
    expect(claim.proof_source.path.length).toBeGreaterThan(0);
    if (claim.status === "proved") {
      expect(claim.verification).toBeDefined();
      expect(claim.verification!.sorries).toBe(0);
      expect(claim.proof_source.commit).toMatch(COMMIT_RE);
      for (const ax of claim.verification!.axioms) {
        expect(STANDARD_AXIOMS.has(ax), `${claim.claim_id}: non-standard axiom ${ax}`).toBe(true);
      }
    }
    if (claim.status === "conditional") {
      expect(claim.conditional_on?.length ?? 0).toBeGreaterThan(0);
    }
  }
}

describe("formal-claims contract (v1)", () => {
  it("packaged snapshot satisfies catalog invariants", () => {
    catalogInvariants(catalog);
  });

  it("fixture catalog satisfies catalog invariants", () => {
    catalogInvariants(fixtureJson as unknown as FormalClaimsCatalog);
  });

  it("only proved entries can ever be labeled formally verified", () => {
    const view = formalClaims;
    for (const claim of catalog.claims) {
      expect(view.isFormallyVerified(claim.claim_id)).toBe(claim.status === "proved");
    }
    expect(view.isFormallyVerified("Leibniz.DoesNotExist.thing")).toBe(false);
  });

  it("display objects separate sourced explanation from verified proof", () => {
    for (const claim of catalog.claims) {
      const display = formalClaims.describeClaim(claim.claim_id)!;
      expect(display.sourced_explanation.length).toBeGreaterThan(0);
      if (claim.status === "proved") {
        expect(display.verified_provenance).not.toBeNull();
        expect(display.verified_provenance!.commit).toMatch(COMMIT_RE);
      } else {
        expect(display.verified_provenance).toBeNull();
      }
    }
  });

  it("fixture gate semantics: conditional/informal/open are never verified", () => {
    const view = createCatalogView(fixtureJson as unknown as FormalClaimsCatalog);
    const proved = fixtureJson.claims.find((c) => c.status === "proved") as FormalClaim;
    expect(view.isFormallyVerified(proved.claim_id)).toBe(true);
    for (const c of fixtureJson.claims.filter((x) => x.status !== "proved")) {
      expect(view.isFormallyVerified(c.claim_id)).toBe(false);
      expect(view.describeClaim(c.claim_id)!.verified_provenance).toBeNull();
    }
    expect(view.describeClaim("no.such.claim")).toBeNull();
  });

  it("status labels are honest, human-facing, and never overclaim", () => {
    expect(statusLabel("proved")).toContain("Formally verified");
    expect(statusLabel("conditional")).toContain("Conditional");
    expect(statusLabel("informal")).toContain("Informal");
    expect(statusLabel("open_problem")).toContain("Open problem");
  });

  it("text matching never invents claims outside the catalog", () => {
    const matches = formalClaims.matchClaimsInText(
      "tell me about tensio_symm and Leibniz.OpenProblems.wilson-loop",
    );
    for (const m of matches) {
      expect(catalog.claims.some((c) => c.claim_id === m.claim_id)).toBe(true);
    }
  });

  it("router exposes the catalog read-only (queries, no mutations)", async () => {
    // The catalog snapshot must not be mutated by any router call.
    const before = JSON.stringify(catalog);
    const caller = appRouter.createCaller({
      user: null,
      req: {} as never,
      res: { clearCookie: () => {} } as never,
    });
    const list = await caller.formalClaims.list();
    expect(list.schema_version).toBe(CATALOG_SCHEMA_VERSION);
    const proved = list.claims.find((c) => c.formally_verified);
    expect(proved?.status).toBe("proved");

    const byId = await caller.formalClaims.byId({ claim_id: proved!.claim_id });
    expect(byId.found).toBe(true);

    const missing = await caller.formalClaims.byId({ claim_id: "no.such.claim" });
    expect(missing.found).toBe(false);

    expect(JSON.stringify(catalog)).toBe(before);
  });
});

describe("catalog presentation (v1.1 UI surfacing)", () => {
  const catalogs: [string, FormalClaimsCatalog][] = [
    ["snapshot", catalog],
    ["fixture", fixtureJson as unknown as FormalClaimsCatalog],
  ];

  for (const [name, cat] of catalogs) {
    it(`${name}: grouping covers every claim exactly once, modules consistent`, () => {
      const groups = groupByModule(cat.claims);
      const grouped = groups.flatMap((g) => g.claims.map((c) => c.claim_id));
      expect(grouped.length).toBe(cat.claims.length);
      expect(new Set(grouped).size).toBe(cat.claims.length);
      for (const g of groups) {
        expect(g.claims.every((c) => c.module === g.module)).toBe(true);
      }
    });

    it(`${name}: stats match the catalog and total is conserved`, () => {
      const stats = catalogStats(cat.claims);
      expect(stats.total).toBe(cat.claims.length);
      const recount = { proved: 0, conditional: 0, informal: 0, open_problem: 0 };
      for (const c of cat.claims) recount[c.status]++;
      expect(stats.proved).toBe(recount.proved);
      expect(stats.conditional).toBe(recount.conditional);
      expect(stats.informal).toBe(recount.informal);
      expect(stats.open_problem).toBe(recount.open_problem);
    });

    it(`${name}: claim rows stay honest — formally_verified iff proved`, () => {
      for (const c of cat.claims) {
        const row = toClaimRow(c, statusLabel);
        expect(row.formally_verified).toBe(c.status === "proved");
        expect(row.status_label).toBe(statusLabel(c.status));
      }
    });

    it(`${name}: status filter selects exactly its status (or all)`, () => {
      for (const f of ["all", "proved", "conditional", "informal", "open_problem"] as const) {
        const selected = cat.claims.filter((c) => matchesFilter(c, f));
        expect(selected.length).toBe(f === "all" ? cat.claims.length : catalogStats(cat.claims)[f]);
      }
    });
  }

  it("router list endpoint: formally_verified only for proved entries", async () => {
    const caller = appRouter.createCaller({} as never); // public procedure: no ctx used
    const result = (await caller.formalClaims.list()) as unknown as {
      claims: { claim_id: string; status: string; formally_verified: boolean }[];
    };
    expect(result.claims.length).toBe(catalog.claims.length);
    for (const c of result.claims) {
      expect(c.formally_verified).toBe(c.status === "proved");
    }
  });
});
