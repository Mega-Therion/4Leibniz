/**
 * Contract test for the formal-claims consumer (4Leibniz issue #11).
 *
 * Run: npm run test:contract   (plain tsx script — no test framework needed)
 *
 * Asserts, against BOTH the packaged snapshot and a self-contained fixture:
 *   1. catalog invariants (v1, controlled statuses, sorted unique ids,
 *      proved ⇒ verification with sorries=0 and 40-hex commit provenance),
 *   2. the consumer gate: only catalog `proved` entries can ever be
 *      labeled formally verified; everything else — conditional, informal,
 *      open_problem, unknown — is structurally incapable of it,
 *   3. display objects separate sourced explanation from verified proof.
 */
import * as assert from 'node:assert/strict';
import {
  catalog,
  createCatalogView,
  CATALOG_SCHEMA_VERSION,
  listClaims,
  statusLabel,
  type FormalClaim,
  type FormalClaimsCatalog,
} from '@/lib/formal-claims';
import {
  catalogStats,
  groupByModule,
  statusChipVariant,
  toClaimCardModel,
} from '@/lib/formal-claims/presentation';
import fixtureJson from './fixtures/formal-claims/formal-claims-v1.fixture.json';

let failures = 0;
function check(name: string, fn: () => void) {
  try {
    fn();
    console.log(`  ok  ${name}`);
  } catch (error) {
    failures++;
    console.error(`FAIL  ${name}: ${(error as Error).message}`);
  }
}

const STATUSES = new Set(['proved', 'conditional', 'informal', 'open_problem']);
const STANDARD_AXIOMS = new Set(['propext', 'Classical.choice', 'Quot.sound']);
const COMMIT_RE = /^[0-9a-f]{40}$/;

function catalogInvariants(name: string, cat: FormalClaimsCatalog) {
  check(`${name}: schema_version is v1`, () => {
    assert.equal(cat.schema_version, CATALOG_SCHEMA_VERSION);
    assert.equal(cat.generator.name.length > 0, true);
  });
  check(`${name}: source is commit-pinned (40-hex)`, () => {
    assert.match(cat.source.commit, COMMIT_RE);
    assert.equal(cat.source.repository, 'Mega-Therion/4Leibniz');
    assert.equal(typeof cat.source.lean_toolchain, 'string');
  });
  check(`${name}: claim ids sorted and unique`, () => {
    const ids = cat.claims.map((c) => c.claim_id);
    assert.deepEqual(ids, [...ids].sort());
    assert.equal(ids.length, new Set(ids).size);
  });
  check(`${name}: statuses are controlled vocabulary only`, () => {
    for (const claim of cat.claims) assert.ok(STATUSES.has(claim.status));
  });
  check(`${name}: every proved claim carries real verification`, () => {
    for (const claim of cat.claims) {
      if (claim.status !== 'proved') continue;
      assert.ok(claim.verification, `${claim.claim_id}: missing verification`);
      assert.equal(claim.verification.sorries, 0);
      assert.match(claim.proof_source.commit, COMMIT_RE);
      for (const ax of claim.verification.axioms) {
        assert.ok(
          STANDARD_AXIOMS.has(ax),
          `${claim.claim_id}: proved with non-standard axiom ${ax}`,
        );
      }
    }
  });
  check(`${name}: conditional claims record their assumptions`, () => {
    for (const claim of cat.claims) {
      if (claim.status === 'conditional') {
        assert.ok(
          claim.conditional_on && claim.conditional_on.length > 0,
          `${claim.claim_id}: conditional without conditional_on`,
        );
      }
    }
  });
  check(`${name}: every claim has source_refs and a proof_source path`, () => {
    for (const claim of cat.claims) {
      assert.ok(claim.source_refs.length > 0, claim.claim_id);
      assert.ok(claim.proof_source.path.length > 0, claim.claim_id);
    }
  });
}

function gateSemantics(name: string, cat: FormalClaimsCatalog) {
  const view = createCatalogView(cat);
  const proved = cat.claims.find((c) => c.status === 'proved');
  const conditional = cat.claims.find((c) => c.status === 'conditional');
  const informal = cat.claims.find((c) => c.status === 'informal');
  const open = cat.claims.find((c) => c.status === 'open_problem');

  check(`${name}: proved claim is formally verified`, () => {
    assert.ok(proved, 'fixture must contain a proved claim');
    assert.equal(view.isFormallyVerified((proved as FormalClaim).claim_id), true);
  });
  check(`${name}: conditional is NOT formally verified`, () => {
    if (conditional)
      assert.equal(view.isFormallyVerified(conditional.claim_id), false);
  });
  check(`${name}: informal is NOT formally verified`, () => {
    if (informal) assert.equal(view.isFormallyVerified(informal.claim_id), false);
  });
  check(`${name}: open_problem is NOT formally verified`, () => {
    if (open) assert.equal(view.isFormallyVerified(open.claim_id), false);
  });
  check(`${name}: unknown id is NOT formally verified`, () => {
    assert.equal(view.isFormallyVerified('Leibniz.DoesNotExist.thing'), false);
  });
  check(`${name}: display separates explanation from verified proof`, () => {
    const dProved = view.describeClaim((proved as FormalClaim).claim_id);
    assert.ok(dProved);
    assert.ok(dProved.verified_provenance, 'proved display must carry provenance');
    assert.match(dProved.verified_provenance!.commit, COMMIT_RE);
    assert.ok(dProved.sourced_explanation.length > 0);

    for (const c of [conditional, informal, open]) {
      if (!c) continue;
      const d = view.describeClaim(c.claim_id);
      assert.ok(d, c.claim_id);
      assert.equal(
        d.verified_provenance,
        null,
        `${c.claim_id} (${c.status}) must not carry verified provenance`,
      );
    }
  });
  check(`${name}: text matching never invents claims`, () => {
    const matches = view.matchClaimsInText(
      'tell me about tensio_symm and Leibniz.OpenProblems.wilson-loop',
    );
    for (const m of matches) {
      assert.ok(cat.claims.some((c) => c.claim_id === m.claim_id));
    }
  });
}

console.log('formal-claims consumer contract tests');
// ---------------------------------------------------------------------------
// v1.1 presentation layer: grouping, stats, and card models must stay honest.
// ---------------------------------------------------------------------------
{
  const claims = catalog.claims;
  const groups = groupByModule(claims);

  check('presentation: grouping covers every claim exactly once', () => {
    const grouped = groups.flatMap((g) => g.claims.map((c) => c.claim_id));
    assert.equal(grouped.length, claims.length);
    assert.equal(new Set(grouped).size, claims.length);
    for (const g of groups) {
      for (const c of g.claims) assert.equal(c.module, g.module);
    }
  });

  check('presentation: stats match the catalog', () => {
    const stats = catalogStats(claims);
    assert.equal(stats.total, claims.length);
    const recount = { proved: 0, conditional: 0, informal: 0, open_problem: 0 };
    for (const c of claims) recount[c.status]++;
    assert.deepEqual(
      { proved: stats.proved, conditional: stats.conditional, informal: stats.informal, open_problem: stats.open_problem },
      recount,
    );
  });

  check('presentation: card models never invent verified provenance', () => {
    for (const c of claims) {
      const card = toClaimCardModel(c, statusLabel);
      assert.equal(card.claim_id, c.claim_id);
      assert.equal(card.status_label, statusLabel(c.status));
      if (c.status === 'proved') {
        assert.ok(card.verified_provenance, 'proved claim must carry provenance');
        assert.match(card.verified_provenance.commit, COMMIT_RE);
      } else {
        assert.equal(card.verified_provenance, null, `${c.claim_id} must not carry provenance`);
      }
    }
  });

  check('presentation: chip variants stay honest (proved=gold only)', () => {
    assert.equal(statusChipVariant('proved'), 'gold');
    assert.notEqual(statusChipVariant('conditional'), 'gold');
    assert.notEqual(statusChipVariant('open_problem'), 'gold');
    assert.notEqual(statusChipVariant('informal'), 'gold');
  });
}

catalogInvariants('packaged snapshot', catalog);
gateSemantics('packaged snapshot', catalog);
catalogInvariants('fixture catalog', fixtureJson as unknown as FormalClaimsCatalog);
gateSemantics('fixture catalog', fixtureJson as unknown as FormalClaimsCatalog);

if (failures > 0) {
  console.error(`\\n${failures} contract check(s) FAILED`);
  process.exit(1);
}
console.log('\\nAll contract checks passed.');
