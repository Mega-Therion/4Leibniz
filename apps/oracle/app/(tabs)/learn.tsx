import { useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { lessons, repoModules, type RepoModule } from "@/lib/leibniz-data";
import { useColors } from "@/hooks/use-colors";
import { useProgress } from "@/lib/progress-context";

export default function LearnScreen() {
  const colors = useColors();
  const progress = useProgress();
  const [selected, setSelected] = useState<RepoModule | null>(null);

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.headerRow}>
          <View><Text style={[styles.eyebrow, { color: colors.primary }]}>THE LIBRARY</Text><Text style={[styles.title, { color: colors.foreground }]}>Follow the thread.</Text></View>
          <View style={[styles.counter, { backgroundColor: colors.surface, borderColor: colors.border }]}><Text style={[styles.counterText, { color: colors.foreground }]}>{repoModules.length} paths</Text></View>
        </View>
        <Text style={[styles.intro, { color: colors.muted }]}>Begin with the history, then descend into the formal vocabulary. Every module is a doorway between a philosophical idea and a runnable artifact.</Text>

        <View style={[styles.progressCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={styles.progressTop}><View><Text style={[styles.progressEyebrow, { color: colors.primary }]}>YOUR TRAJECTORY</Text><Text style={[styles.progressTitle, { color: colors.foreground }]}>{progress.completedCount} of {lessons.length} lessons completed</Text></View><Text style={[styles.progressPercent, { color: colors.primary }]}>{progress.progressPercent}%</Text></View>
          <View style={[styles.track, { backgroundColor: colors.border }]}><View style={[styles.fill, { width: `${progress.progressPercent}%`, backgroundColor: colors.primary }]} /></View>
          <View style={styles.progressBottom}><Text style={[styles.progressMeta, { color: colors.muted }]}>{progress.bookmarkedCount} saved for later</Text><Text style={[styles.progressMeta, { color: colors.muted }]}>{progress.nextMilestone ? `Next: ${progress.nextMilestone.label}` : "Library complete"}</Text></View>
        </View>

        <View style={[styles.featureCard, { backgroundColor: "#172B2D", borderColor: "#315452" }]}>
          <View style={styles.featureTop}><Text style={styles.featureKicker}>GUIDED READING</Text><Text style={styles.featureTag}>01 / 03</Text></View>
          <Text style={styles.featureTitle}>What does a proof assistant change about philosophy?</Text>
          <Text style={styles.featureBody}>A short field guide to Leibniz, formal methods, and the discipline of stating exactly what a theorem does—and does not—say.</Text>
          <Pressable onPress={() => router.push("/(tabs)/guide")} style={({ pressed }) => [styles.featureButton, pressed && styles.pressed]}><Text style={styles.featureButtonText}>Discuss with the Oracle</Text><IconSymbol name="chevron.right" size={17} color="#172B2D" /></Pressable>
        </View>

        <View style={[styles.featureCard, { backgroundColor: "#172B2D", borderColor: "#315452" }]}>
          <View style={styles.featureTop}><Text style={styles.featureKicker}>PROOF-GROUNDED CATALOG</Text><Text style={styles.featureTag}>VERIFIED STATUS</Text></View>
          <Text style={styles.featureTitle}>What has actually been proved?</Text>
          <Text style={styles.featureBody}>Every formal claim in 4Leibniz, each labeled by the pinned Lean toolchain as proved, conditional, or open — with the commit and axioms behind it. No claim is ever displayed as more verified than it is.</Text>
          <Pressable onPress={() => router.push("/catalog")} style={({ pressed }) => [styles.featureButton, pressed && styles.pressed]}><Text style={styles.featureButtonText}>Browse the catalog</Text><IconSymbol name="chevron.right" size={17} color="#172B2D" /></Pressable>
        </View>

        <Text style={[styles.sectionEyebrow, { color: colors.muted }]}>LEIBNIZ IN THREE MOVES</Text>
        {lessons.map((lesson, index) => {
          const lessonId = lesson.title;
          const bookmarked = progress.isBookmarked(lessonId);
          const complete = progress.isComplete(lessonId);
          return <View key={lesson.title} style={[styles.lessonCard, { backgroundColor: colors.surface, borderColor: complete ? colors.success + "90" : colors.border }]}>
            <View style={[styles.lessonNumber, { backgroundColor: lesson.accent }]}><Text style={styles.lessonNumberText}>0{index + 1}</Text></View>
            <View style={styles.lessonCopy}><View style={styles.lessonMetaRow}><Text style={[styles.lessonCategory, { color: colors.muted }]}>{lesson.category} · {lesson.duration}</Text><Pressable onPress={() => progress.toggleBookmark(lessonId)} hitSlop={8}><IconSymbol name="bookmark.fill" size={17} color={bookmarked ? colors.primary : colors.muted} /></Pressable></View><Text style={[styles.lessonTitle, { color: colors.foreground }]}>{lesson.title}</Text><Text style={[styles.lessonBody, { color: colors.muted }]} numberOfLines={3}>{lesson.body}</Text><View style={styles.lessonActions}><Pressable onPress={() => progress.toggleComplete(lessonId)} style={({ pressed }) => [styles.completeButton, { backgroundColor: complete ? colors.success + "18" : colors.background, borderColor: complete ? colors.success + "70" : colors.border }, pressed && styles.pressed]}><Text style={[styles.completeText, { color: complete ? colors.success : colors.muted }]}>{complete ? "Completed" : "Mark complete"}</Text></Pressable><Pressable onPress={() => router.push("/(tabs)/guide")}><Text style={[styles.readLink, { color: colors.primary }]}>Ask about this →</Text></Pressable></View></View>
          </View>;
        })}

        <View style={styles.sectionLine}><Text style={[styles.sectionEyebrow, { color: colors.muted }]}>REPO MODULES</Text><Text style={[styles.sectionNote, { color: colors.muted }]}>Tap to open a field note</Text></View>
        {repoModules.map((module) => <Pressable key={module.name} onPress={() => setSelected(selected?.name === module.name ? null : module)} style={({ pressed }) => [styles.moduleCard, { backgroundColor: colors.surface, borderColor: selected?.name === module.name ? module.color : colors.border }, pressed && styles.pressed]}><View style={[styles.moduleIcon, { backgroundColor: module.color + "28" }]}><IconSymbol name={module.kind === "python" ? "chevron.left.forwardslash.chevron.right" : module.kind === "corpus" ? "book.fill" : "flask.fill"} size={19} color={module.color} /></View><View style={styles.moduleText}><Text style={[styles.moduleName, { color: colors.foreground }]}>{module.name}</Text><Text style={[styles.modulePath, { color: colors.muted }]}>{module.path}</Text>{selected?.name === module.name && <><Text style={[styles.moduleDetail, { color: colors.muted }]}>{module.detail}</Text><View style={styles.tagRow}>{module.tags.map(tag => <View key={tag} style={[styles.tag, { backgroundColor: module.color + "20" }]}><Text style={[styles.tagText, { color: module.color }]}>{tag}</Text></View>)}</View></>}</View><IconSymbol name="chevron.right" size={18} color={colors.muted} /></Pressable>)}
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  content: { padding: 22, paddingBottom: 45, gap: 14 },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" },
  eyebrow: { fontSize: 10, letterSpacing: 1.7, fontWeight: "800" },
  title: { fontSize: 29, fontWeight: "800", letterSpacing: -0.7, marginTop: 4 },
  counter: { borderWidth: 1, borderRadius: 20, paddingHorizontal: 11, paddingVertical: 6 },
  counterText: { fontSize: 11, fontWeight: "700" },
  intro: { fontSize: 14, lineHeight: 21, marginBottom: 4 },
  progressCard: { borderRadius: 17, borderWidth: 1, padding: 14 },
  progressTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" },
  progressEyebrow: { fontSize: 9, letterSpacing: 1.5, fontWeight: "900" },
  progressTitle: { fontSize: 15, fontWeight: "800", marginTop: 4 },
  progressPercent: { fontSize: 22, fontWeight: "900" },
  track: { height: 7, borderRadius: 4, overflow: "hidden", marginTop: 13 },
  fill: { height: "100%", borderRadius: 4 },
  progressBottom: { flexDirection: "row", justifyContent: "space-between", marginTop: 8 },
  progressMeta: { fontSize: 10 },
  featureCard: { borderRadius: 22, padding: 20, marginBottom: 13 },
  featureTop: { flexDirection: "row", justifyContent: "space-between" },
  featureKicker: { color: "#A9D4CB", fontSize: 10, letterSpacing: 1.7, fontWeight: "800" },
  featureTag: { color: "#779B97", fontSize: 11 },
  featureTitle: { color: "#F4EAD5", fontSize: 23, lineHeight: 28, fontWeight: "800", marginTop: 26, letterSpacing: -0.4 },
  featureBody: { color: "#B4C6C0", fontSize: 13, lineHeight: 20, marginTop: 10 },
  featureButton: { alignSelf: "flex-start", backgroundColor: "#E9B872", borderRadius: 13, paddingVertical: 11, paddingHorizontal: 14, flexDirection: "row", alignItems: "center", gap: 9, marginTop: 18 },
  featureButtonText: { color: "#172B2D", fontWeight: "800", fontSize: 12 },
  pressed: { opacity: 0.72, transform: [{ scale: 0.985 }] },
  sectionEyebrow: { fontSize: 10, letterSpacing: 1.55, fontWeight: "800", marginTop: 8 },
  lessonCard: { borderWidth: 1, borderRadius: 16, padding: 14, flexDirection: "row", gap: 13 },
  lessonNumber: { width: 33, height: 33, borderRadius: 10, alignItems: "center", justifyContent: "center" },
  lessonNumberText: { color: "#172B2D", fontSize: 12, fontWeight: "900" },
  lessonCopy: { flex: 1 },
  lessonMetaRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  lessonCategory: { fontSize: 10, letterSpacing: 0.9, textTransform: "uppercase", fontWeight: "800" },
  lessonTitle: { fontSize: 16, fontWeight: "800", marginTop: 4 },
  lessonBody: { fontSize: 12, lineHeight: 18, marginTop: 6 },
  lessonActions: { flexDirection: "row", alignItems: "center", gap: 12, marginTop: 10 },
  completeButton: { borderRadius: 9, borderWidth: 1, paddingHorizontal: 8, paddingVertical: 6 },
  completeText: { fontSize: 10, fontWeight: "800" },
  readLink: { fontSize: 12, fontWeight: "800" },
  sectionLine: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginTop: 11 },
  sectionNote: { fontSize: 11 },
  moduleCard: { borderWidth: 1, borderRadius: 15, padding: 13, flexDirection: "row", alignItems: "flex-start", gap: 11 },
  moduleIcon: { width: 35, height: 35, borderRadius: 11, alignItems: "center", justifyContent: "center" },
  moduleText: { flex: 1 },
  moduleName: { fontSize: 15, fontWeight: "800" },
  modulePath: { fontFamily: "monospace", fontSize: 10, marginTop: 3 },
  moduleDetail: { fontSize: 12, lineHeight: 18, marginTop: 10 },
  tagRow: { flexDirection: "row", gap: 6, flexWrap: "wrap", marginTop: 9 },
  tag: { borderRadius: 8, paddingHorizontal: 7, paddingVertical: 4 },
  tagText: { fontSize: 10, fontWeight: "800" },
});
