import type { Metadata } from 'next';
import { SectionFrame } from '@/components/SectionFrame';
import { ClaimCatalog } from '@/components/ClaimCatalog';
import { catalog, listClaims, statusLabel } from '@/lib/formal-claims';
import { catalogStats, groupByModule, toClaimCardModel } from '@/lib/formal-claims/presentation';

export const metadata: Metadata = {
  title: 'Proof-grounded catalog',
  description:
    'Every formal claim catalogued by the 4Leibniz proof engine: what is proved under the pinned Lean toolchain, what is conditional and on what, and what remains open.',
  alternates: { canonical: '/catalog' },
};

export default function CatalogPage() {
  const claims = listClaims();
  const stats = catalogStats(claims);
  const groups = groupByModule(claims).map((g) => ({
    module: g.module,
    claims: g.claims.map((c) => toClaimCardModel(c, statusLabel)),
  }));

  const statLine = `${stats.proved} proved · ${stats.conditional} conditional · ${stats.open_problem} open problems`;

  return (
    <SectionFrame
      eyebrow="Proof-grounded catalog"
      title="Every claim, checked."
      description={`This page surfaces the formal-claims catalog produced by the 4Leibniz proof engine at commit ${catalog.source.commit.slice(0, 12)} — read-only, never re-derived here. A claim is labeled formally verified only when the pinned Lean toolchain proved it. Everything else keeps its honest status: conditional on recorded assumptions, or an open problem.`}
      className="pt-s12"
    >
      <p className="label mt-s2">{statLine}</p>
      <ClaimCatalog groups={groups} />
      <footer className="mt-s10 border-t border-line2 pt-s6 text-xs leading-relaxed text-text3">
        <p>
          Catalog {catalog.schema_version}, generated {catalog.generated_at} by{' '}
          {catalog.generator.name} v{catalog.generator.version} · source{' '}
          {catalog.source.repository} at commit{' '}
          <span className="font-mono">{catalog.source.commit.slice(0, 12)}</span> · Lean
          toolchain {catalog.source.lean_toolchain} · lake build exit{' '}
          {catalog.verification_record.lake_build_exit_code ?? 'n/a'} ·{' '}
          {catalog.verification_record.sorries} sorry. This archive is a consumer: it
          displays the catalog; it never elevates a claim.
        </p>
      </footer>
    </SectionFrame>
  );
}
