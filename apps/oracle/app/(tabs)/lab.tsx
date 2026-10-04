import { useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { claimExamples, type ClaimExample } from "@/lib/leibniz-data";
import { useColors } from "@/hooks/use-colors";

const verdictMeta = {
  proved: { label: "KERNEL-PROVEN", color: "#79C8A9", icon: "✓" },
  open: { label: "OPEN / MEASURE", color: "#E9B872", icon: "?" },
  caution: { label: "READ WITH CAUTION", color: "#E58B81", icon: "!" },
};

export default function LabScreen() {
  const colors = useColors();
  const [selected, setSelected] = useState<ClaimExample>(claimExamples[0]);
  const [ran, setRan] = useState(false);

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={[styles.eyebrow, { color: colors.primary }]}>CALCULEMUS / LAB</Text>
        <Text style={[styles.title, { color: colors.foreground }]}>Make a claim.</Text>
        <Text style={[styles.intro, { color: colors.muted }]}>This is a conceptual simulator of the repo's claim → kernel workflow. Select a case, run it, and inspect the boundary between a valid theorem and a story that needs more evidence.</Text>

        <View style={[styles.pipeline, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          {["CLAIM", "IR", "RULES", "KERNEL"].map((step, index) => <View key={step} style={styles.pipelineStep}><View style={[styles.pipelineDot, { backgroundColor: index < 3 ? colors.primary : colors.success }]}><Text style={styles.pipelineNumber}>{index + 1}</Text></View><Text style={[styles.pipelineLabel, { color: colors.muted }]}>{step}</Text>{index < 3 && <View style={[styles.pipelineLine, { backgroundColor: colors.border }]} />}</View>)}
        </View>

        <Text style={[styles.sectionLabel, { color: colors.muted }]}>CHOOSE AN EXPERIMENT</Text>
        {claimExamples.map((claim) => { const active = selected.title === claim.title; return <Pressable key={claim.title} onPress={() => { setSelected(claim); setRan(false); }} style={({ pressed }) => [styles.claimCard, { backgroundColor: active ? colors.primary + "16" : colors.surface, borderColor: active ? colors.primary : colors.border }, pressed && styles.pressed]}><View style={[styles.claimIndicator, { backgroundColor: verdictMeta[claim.verdict].color }]} /><View style={styles.claimCopy}><Text style={[styles.claimTitle, { color: colors.foreground }]}>{claim.title}</Text><Text style={[styles.claimPrompt, { color: colors.muted }]}>{claim.prompt}</Text></View><IconSymbol name="chevron.right" size={18} color={active ? colors.primary : colors.muted} /></Pressable>; })}

        <View style={[styles.console, { backgroundColor: "#121A1D", borderColor: "#304047" }]}>
          <View style={styles.consoleHeader}><View style={styles.consoleDots}><View style={[styles.consoleDot, { backgroundColor: "#E58B81" }]} /><View style={[styles.consoleDot, { backgroundColor: "#E9B872" }]} /><View style={[styles.consoleDot, { backgroundColor: "#79C8A9" }]} /></View><Text style={styles.consoleTitle}>oracle / adjudication</Text></View>
          <Text style={styles.consolePrompt}>{"> "}{selected.prompt}</Text>
          <Text style={styles.consoleCode}>{selected.code}</Text>
          {!ran ? <Pressable onPress={() => setRan(true)} style={({ pressed }) => [styles.runButton, { backgroundColor: colors.primary }, pressed && styles.pressed]}><Text style={styles.runButtonText}>Run transparent check</Text><IconSymbol name="chevron.right" size={17} color="#121A1D" /></Pressable> : <View style={[styles.verdict, { borderColor: verdictMeta[selected.verdict].color + "80" }]}><View style={[styles.verdictMark, { backgroundColor: verdictMeta[selected.verdict].color }]}><Text style={styles.verdictMarkText}>{verdictMeta[selected.verdict].icon}</Text></View><View style={{ flex: 1 }}><Text style={[styles.verdictLabel, { color: verdictMeta[selected.verdict].color }]}>{verdictMeta[selected.verdict].label}</Text><Text style={styles.verdictBody}>{selected.explanation}</Text></View></View>}
        </View>

        <View style={[styles.note, { backgroundColor: colors.warning + "13", borderColor: colors.warning + "44" }]}><IconSymbol name="sparkles" size={20} color={colors.warning} /><Text style={[styles.noteText, { color: colors.foreground }]}><Text style={{ fontWeight: "800" }}>The rule of this lab: </Text>never confuse a green build with a verified world. Ask what was assumed, what was measured, and what the kernel actually checked.</Text></View>
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  content: { padding: 22, paddingBottom: 50, gap: 13 },
  eyebrow: { fontSize: 10, letterSpacing: 1.7, fontWeight: "800" },
  title: { fontSize: 30, fontWeight: "800", letterSpacing: -0.7, marginTop: 4 },
  intro: { fontSize: 14, lineHeight: 21 },
  pipeline: { borderWidth: 1, borderRadius: 16, padding: 14, flexDirection: "row", justifyContent: "space-between", marginTop: 3 },
  pipelineStep: { flexDirection: "row", alignItems: "center", flex: 1 },
  pipelineDot: { width: 25, height: 25, borderRadius: 13, alignItems: "center", justifyContent: "center" },
  pipelineNumber: { color: "#172B2D", fontWeight: "900", fontSize: 11 },
  pipelineLabel: { fontSize: 9, fontWeight: "800", marginLeft: 5, letterSpacing: 0.4 },
  pipelineLine: { height: 1, flex: 1, marginHorizontal: 7 },
  sectionLabel: { fontSize: 10, letterSpacing: 1.5, fontWeight: "800", marginTop: 10 },
  claimCard: { borderWidth: 1, minHeight: 65, borderRadius: 15, padding: 12, flexDirection: "row", alignItems: "center", gap: 11 },
  claimIndicator: { width: 6, height: 37, borderRadius: 4 },
  claimCopy: { flex: 1 },
  claimTitle: { fontSize: 14, fontWeight: "800" },
  claimPrompt: { fontSize: 11, marginTop: 3 },
  pressed: { opacity: 0.72, transform: [{ scale: 0.985 }] },
  console: { borderWidth: 1, borderRadius: 17, overflow: "hidden", marginTop: 5 },
  consoleHeader: { flexDirection: "row", alignItems: "center", padding: 13, borderBottomWidth: 1, borderBottomColor: "#304047", gap: 9 },
  consoleDots: { flexDirection: "row", gap: 5 },
  consoleDot: { width: 7, height: 7, borderRadius: 4 },
  consoleTitle: { color: "#8EA19F", fontSize: 10, fontFamily: "monospace" },
  consolePrompt: { color: "#E9B872", fontSize: 12, fontFamily: "monospace", lineHeight: 18, padding: 14, paddingBottom: 4 },
  consoleCode: { color: "#B8C8C2", fontSize: 11, lineHeight: 17, fontFamily: "monospace", paddingHorizontal: 14, paddingBottom: 14 },
  runButton: { alignSelf: "flex-start", flexDirection: "row", alignItems: "center", gap: 8, borderRadius: 11, paddingVertical: 10, paddingHorizontal: 13, marginHorizontal: 14, marginBottom: 15 },
  runButtonText: { color: "#121A1D", fontSize: 12, fontWeight: "900" },
  verdict: { margin: 14, marginTop: 0, padding: 12, borderRadius: 12, borderWidth: 1, flexDirection: "row", gap: 10 },
  verdictMark: { width: 25, height: 25, borderRadius: 13, alignItems: "center", justifyContent: "center" },
  verdictMarkText: { color: "#121A1D", fontSize: 15, fontWeight: "900" },
  verdictLabel: { fontSize: 10, letterSpacing: 1, fontWeight: "900" },
  verdictBody: { color: "#CBD6D2", fontSize: 12, lineHeight: 18, marginTop: 4 },
  note: { borderWidth: 1, borderRadius: 15, padding: 13, flexDirection: "row", gap: 10, marginTop: 3 },
  noteText: { flex: 1, fontSize: 12, lineHeight: 18 },
});
