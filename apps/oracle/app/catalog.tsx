import { useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { trpc } from "@/lib/trpc";
import { useColors } from "@/hooks/use-colors";
import {
  groupByModule,
  matchesFilter,
  type ClaimRow,
  type ModuleGroup,
  type StatusFilter,
} from "@/shared/catalog-presentation";

const FILTERS: { key: StatusFilter; label: string }[] = [
  { key: "all", label: "All" },
  { key: "proved", label: "Verified" },
  { key: "conditional", label: "Conditional" },
  { key: "open_problem", label: "Open" },
];

/**
 * The proof-grounded catalog (v1.1): every formal claim with its honest
 * status. Read-only consumer of the tRPC router; `formally_verified` comes
 * from the server, which derives it only from catalog `proved` entries.
 */
export default function CatalogScreen() {
  const colors = useColors();
  const [filter, setFilter] = useState<StatusFilter>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const list = trpc.formalClaims.list.useQuery();
  const detail = trpc.formalClaims.byId.useQuery(
    { claim_id: selectedId ?? "__none__" },
    { enabled: selectedId !== null },
  );

  const claims = list.data?.claims ?? [];
  const groups: ModuleGroup<ClaimRow>[] = groupByModule(claims)
    .map((g) => ({ module: g.module, claims: g.claims.filter((c) => matchesFilter(c, filter)) }))
    .filter((g) => g.claims.length > 0);

  const selectedCard = detail.data?.found ? detail.data.claim : null;

  return (
    <ScreenContainer>
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <Pressable onPress={() => router.back()} hitSlop={12} style={styles.backButton}>
          <IconSymbol name="chevron.left" size={22} color={colors.primary} />
        </Pressable>
        <View>
          <Text style={[styles.eyebrow, { color: colors.primary }]}>PROOF-GROUNDED CATALOG</Text>
          <Text style={[styles.title, { color: colors.foreground }]}>Every claim, checked.</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={[styles.intro, { color: colors.muted }]}>
          Every formal claim from the 4Leibniz proof engine, with its verified status exactly as the pinned Lean toolchain recorded it —
          {list.data ? ` ${list.data.schema_version}, commit ${list.data.source.commit.slice(0, 12)}` : ""}. The Oracle displays this
          catalog; it never re-derives or elevates a claim.
        </Text>

        <View style={styles.filterRow}>
          {FILTERS.map((f) => (
            <Pressable
              key={f.key}
              onPress={() => setFilter(f.key)}
              style={[
                styles.chip,
                { borderColor: filter === f.key ? colors.primary : colors.border },
                filter === f.key && { backgroundColor: colors.primary + "22" },
              ]}
            >
              <Text style={[styles.chipText, { color: filter === f.key ? colors.primary : colors.muted }]}>{f.label}</Text>
            </Pressable>
          ))}
        </View>

        {list.isLoading && <Text style={[styles.intro, { color: colors.muted }]}>Loading the catalog…</Text>}

        {groups.map((group) => (
          <View key={group.module} style={styles.group}>
            <Text style={[styles.groupName, { color: colors.foreground }]}>{group.module}</Text>
            {group.claims.map((claim) => {
              const open = selectedId === claim.claim_id;
              return (
                <Pressable
                  key={claim.claim_id}
                  onPress={() => setSelectedId(open ? null : claim.claim_id)}
                  style={({ pressed }) => [
                    styles.claimCard,
                    { backgroundColor: colors.surface, borderColor: open ? colors.primary : colors.border },
                    pressed && styles.pressed,
                  ]}
                >
                  <View style={styles.claimTop}>
                    <Text style={[styles.claimTitle, { color: colors.foreground }]}>{claim.title}</Text>
                    <View style={[styles.statusPill, { backgroundColor: claim.formally_verified ? colors.success + "22" : colors.surface }]}>
                      <Text style={[styles.statusText, { color: claim.formally_verified ? colors.success : colors.muted }]}>
                        {claim.status_label}
                      </Text>
                    </View>
                  </View>
                  <Text style={[styles.claimMeta, { color: colors.muted }]}>{claim.module}</Text>

                  {open && (
                    <View style={[styles.detailBox, { borderColor: colors.border }]}>
                      {!open && <Text style={[styles.detailText, { color: colors.muted }]}>{claim.human_summary}</Text>}
                      {selectedCard && selectedCard.claim_id === claim.claim_id && (
                        <>
                          <Text style={[styles.detailLabel, { color: colors.primary }]}>SOURCED EXPLANATION</Text>
                          <Text style={[styles.detailMono, { color: colors.muted }]}>{selectedCard.sourced_explanation}</Text>
                          {selectedCard.verified_provenance && (
                            <>
                              <Text style={[styles.detailLabel, { color: colors.success }]}>PROOF PROVENANCE</Text>
                              <Text style={[styles.detailMono, { color: colors.muted }]}>
                                {selectedCard.verified_provenance.repository} @ {selectedCard.verified_provenance.commit.slice(0, 12)}
                                {"\n"}toolchain {selectedCard.verified_provenance.toolchain}
                                {"\n"}axioms: {selectedCard.verified_provenance.axioms.join(", ")} · zero sorry
                              </Text>
                            </>
                          )}
                          {selectedCard.conditional_on && selectedCard.conditional_on.length > 0 && (
                            <>
                              <Text style={[styles.detailLabel, { color: colors.primary }]}>CONDITIONAL ON</Text>
                              {selectedCard.conditional_on.map((dep: string) => (
                                <Text key={dep} style={[styles.detailMono, { color: colors.muted }]}>
                                  {dep}
                                </Text>
                              ))}
                            </>
                          )}
                        </>
                      )}
                    </View>
                  )}
                </Pressable>
              );
            })}
          </View>
        ))}
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: 8, padding: 18, borderBottomWidth: 1 },
  backButton: { padding: 6, marginLeft: -6 },
  eyebrow: { fontSize: 10, letterSpacing: 1.7, fontWeight: "800" },
  title: { fontSize: 24, fontWeight: "800", letterSpacing: -0.5, marginTop: 3 },
  content: { padding: 22, paddingBottom: 60, gap: 16 },
  intro: { fontSize: 13, lineHeight: 19 },
  filterRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: { borderWidth: 1, borderRadius: 20, paddingHorizontal: 12, paddingVertical: 7 },
  chipText: { fontSize: 12, fontWeight: "700" },
  group: { gap: 10 },
  groupName: { fontSize: 13, fontWeight: "800", letterSpacing: 0.4, marginTop: 6 },
  claimCard: { borderRadius: 15, borderWidth: 1, padding: 14, gap: 7 },
  claimTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", gap: 10 },
  claimTitle: { fontSize: 15, fontWeight: "800", flex: 1, letterSpacing: -0.2 },
  statusPill: { borderRadius: 12, paddingHorizontal: 9, paddingVertical: 4 },
  statusText: { fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  claimMeta: { fontSize: 11 },
  detailBox: { marginTop: 4, borderTopWidth: 1, paddingTop: 10, gap: 7 },
  detailText: { fontSize: 13, lineHeight: 19 },
  detailLabel: { fontSize: 9, letterSpacing: 1.5, fontWeight: "900", marginTop: 4 },
  detailMono: { fontSize: 11, lineHeight: 17, fontFamily: "Courier" },
  pressed: { opacity: 0.78, transform: [{ scale: 0.99 }] },
});
