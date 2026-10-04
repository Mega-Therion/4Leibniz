import { useMemo, useState } from "react";
import { ActivityIndicator, Alert, KeyboardAvoidingView, Platform, Pressable, ScrollView, Share, StyleSheet, Text, TextInput, View } from "react-native";
import * as FileSystem from "expo-file-system/legacy";
import * as Sharing from "expo-sharing";
import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { starterPrompts } from "@/lib/leibniz-data";
import { useColors } from "@/hooks/use-colors";
import { trpc } from "@/lib/trpc";
import { inferTopic, useChatHistory, type ChatMessage, type ChatSession } from "@/lib/chat-history-context";

type Interpretation = { domain: string; task: string; difficulty: string };

const welcome: ChatMessage = { id: "welcome", role: "assistant", content: "Welcome, traveler. I can guide you through the 4Leibniz repository, explain Leibniz's ideas, or help you inspect the difference between a theorem that compiles and a claim that has really been established. Where shall we begin?", bookmarked: false, tags: [], topic: "Repository" };
const fallbackFollowUps = ["What is the core idea here?", "How does this connect to Leibniz?", "Where does the repository formalize this?"];

function makeMessage(role: "user" | "assistant", content: string, profile?: Interpretation | null): ChatMessage {
  return { id: `message-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, role, content, bookmarked: false, tags: [], topic: inferTopic(content, profile) };
}

export default function GuideScreen() {
  const colors = useColors();
  const { sessions, saveSession, deleteSession } = useChatHistory();
  const [messages, setMessages] = useState<ChatMessage[]>([welcome]);
  const [draft, setDraft] = useState("");
  const [tagDraft, setTagDraft] = useState("");
  const [taggingId, setTaggingId] = useState<string | null>(null);
  const [interpretation, setInterpretation] = useState<Interpretation | null>(null);
  const [followUps, setFollowUps] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState(() => `chat-${Date.now()}`);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyQuery, setHistoryQuery] = useState("");
  const [exporting, setExporting] = useState(false);
  const chat = trpc.oracle.chat.useMutation();
  const canSend = draft.trim().length > 0 && !chat.isPending;
  const context = useMemo(() => messages.slice(-8).map(({ role, content }) => ({ role, content })), [messages]);
  const filteredSessions = useMemo(() => {
    const query = historyQuery.trim().toLowerCase();
    if (!query) return sessions;
    return sessions.filter((session) => `${session.title} ${session.profile?.domain ?? ""} ${session.messages.map((message) => `${message.content} ${message.tags.join(" ")}`).join(" ")}`.toLowerCase().includes(query));
  }, [historyQuery, sessions]);
  const bookmarkedCount = messages.filter((message) => message.bookmarked).length;

  function persistSession(nextMessages: ChatMessage[], profile: Interpretation | null) {
    const firstQuestion = nextMessages.find((message) => message.role === "user")?.content ?? "Untitled reflection";
    const title = firstQuestion.length > 46 ? `${firstQuestion.slice(0, 46)}…` : firstQuestion;
    const session: ChatSession = { id: sessionId, title, messages: nextMessages, profile, updatedAt: Date.now() };
    saveSession(session);
  }

  async function send(text = draft) {
    const question = text.trim();
    if (!question || chat.isPending) return;
    setDraft("");
    const next = [...messages, makeMessage("user", question)];
    setMessages(next);
    try {
      const result = await chat.mutateAsync({ messages: context.concat({ role: "user", content: question }) });
      const nextMessages = [...next, makeMessage("assistant", result.answer, result.profile)];
      setInterpretation(result.profile);
      setFollowUps(result.followUps ?? fallbackFollowUps);
      setMessages(nextMessages);
      persistSession(nextMessages, result.profile);
    } catch {
      const nextMessages = [...next, makeMessage("assistant", "I couldn't reach the reasoning engine just now. Try again in a moment, or explore the Library and Lab tabs while the connection returns.", interpretation)];
      setMessages(nextMessages);
      persistSession(nextMessages, interpretation);
    }
  }

  function openSession(session: ChatSession) {
    setSessionId(session.id);
    setMessages(session.messages);
    setInterpretation(session.profile);
    setFollowUps([]);
    setHistoryOpen(false);
  }

  function startNew() {
    setSessionId(`chat-${Date.now()}`);
    setMessages([{ ...welcome, id: `welcome-${Date.now()}` }]);
    setInterpretation(null);
    setFollowUps([]);
    setDraft("");
    setTagDraft("");
    setTaggingId(null);
    setHistoryOpen(false);
  }

  function updateMessage(messageId: string, updater: (message: ChatMessage) => ChatMessage) {
    const nextMessages = messages.map((message) => message.id === messageId ? updater(message) : message);
    setMessages(nextMessages);
    persistSession(nextMessages, interpretation);
  }

  function toggleBookmark(messageId: string) {
    updateMessage(messageId, (message) => ({ ...message, bookmarked: !message.bookmarked }));
  }

  function addTag(messageId: string) {
    const tag = tagDraft.trim().replace(/^#/, "");
    if (!tag) return;
    updateMessage(messageId, (message) => message.tags.includes(tag) ? message : { ...message, tags: [...message.tags, tag].slice(0, 6) });
    setTagDraft("");
    setTaggingId(null);
  }

  function removeTag(messageId: string, tag: string) {
    updateMessage(messageId, (message) => ({ ...message, tags: message.tags.filter((item) => item !== tag) }));
  }

  async function exportThread() {
    if (exporting || messages.length <= 1) return;
    setExporting(true);
    const selected = bookmarkedCount > 0 ? messages.filter((message) => message.bookmarked) : messages.filter((message) => message.id !== "welcome");
    const firstQuestion = messages.find((message) => message.role === "user")?.content ?? "Leibniz Oracle discussion";
    const title = firstQuestion.length > 54 ? `${firstQuestion.slice(0, 54)}…` : firstQuestion;
    const body = [`LEIBNIZ ORACLE`, title, interpretation ? `Lens: ${interpretation.domain} · ${interpretation.task} · ${interpretation.difficulty}` : "", bookmarkedCount > 0 ? "Exported bookmarked insights" : "Exported discussion", "", ...selected.map((message) => `${message.role === "user" ? "YOU" : "ORACLE"}${message.tags.length ? ` [${message.tags.map((tag) => `#${tag}`).join(", ")}]` : ""}\n${message.content}\n`)].join("\n");
    try {
      if (Platform.OS === "web") {
        const blob = new Blob([body], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = "leibniz-oracle-discussion.txt";
        anchor.click();
        URL.revokeObjectURL(url);
      } else {
        const uri = `${FileSystem.cacheDirectory ?? FileSystem.documentDirectory}leibniz-oracle-discussion.txt`;
        await FileSystem.writeAsStringAsync(uri, body, { encoding: FileSystem.EncodingType.UTF8 });
        if (await Sharing.isAvailableAsync()) await Sharing.shareAsync(uri, { mimeType: "text/plain", dialogTitle: "Share Leibniz Oracle discussion" });
        else await Share.share({ message: body, title: "Leibniz Oracle discussion" });
      }
    } catch {
      Alert.alert("Export unavailable", "The discussion could not be exported on this device. You can still copy the key insight into another app.");
    } finally {
      setExporting(false);
    }
  }

  return <ScreenContainer edges={["top", "left", "right", "bottom"]}><KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === "ios" ? "padding" : undefined} keyboardVerticalOffset={8}>
    <View style={styles.header}><View><Text style={[styles.eyebrow, { color: colors.primary }]}>THE ORACLE / LIVE GUIDE</Text><Text style={[styles.title, { color: colors.foreground }]}>Ask anything.</Text></View><View style={styles.headerActions}><Pressable onPress={exportThread} disabled={exporting || messages.length <= 1} style={({ pressed }) => [styles.headerButton, { borderColor: colors.border, backgroundColor: colors.surface, opacity: exporting || messages.length <= 1 ? 0.45 : 1 }, pressed && styles.pressed]}><IconSymbol name="arrow.down.doc.fill" size={15} color={colors.primary} /><Text style={[styles.headerButtonText, { color: colors.foreground }]}>{exporting ? "…" : "Export"}</Text></Pressable><Pressable onPress={() => setHistoryOpen(!historyOpen)} style={({ pressed }) => [styles.headerButton, { borderColor: colors.border, backgroundColor: colors.surface }, pressed && styles.pressed]}><IconSymbol name="clock.fill" size={16} color={colors.primary} /><Text style={[styles.headerButtonText, { color: colors.foreground }]}>{sessions.length}</Text></Pressable><Pressable onPress={startNew} style={({ pressed }) => [styles.headerButton, { borderColor: colors.border, backgroundColor: colors.surface }, pressed && styles.pressed]}><Text style={[styles.newText, { color: colors.primary }]}>New</Text></Pressable></View></View>
    <View style={styles.statusRow}><Text style={[styles.subtitle, { color: colors.muted }]}>Grounded in the repo's modules, README caveats, and Leibniz's conceptual vocabulary.</Text><View style={[styles.online, { borderColor: colors.success + "70" }]}><View style={[styles.onlineDot, { backgroundColor: colors.success }]} /><Text style={[styles.onlineText, { color: colors.success }]}>READY</Text></View></View>
    {interpretation && <View style={[styles.interpretation, { backgroundColor: colors.primary + "12", borderColor: colors.primary + "45" }]}><IconSymbol name="sparkles" size={14} color={colors.primary} /><Text style={[styles.interpretationText, { color: colors.primary }]}>Reading this as {interpretation.domain} · {interpretation.task} · {interpretation.difficulty}</Text></View>}

    {historyOpen ? <View style={[styles.historyPanel, { backgroundColor: colors.surface, borderColor: colors.border }]}><View style={styles.historyTitleRow}><View><Text style={[styles.historyEyebrow, { color: colors.primary }]}>ARCHIVE</Text><Text style={[styles.historyTitle, { color: colors.foreground }]}>Past conversations</Text></View><Text style={[styles.historyCount, { color: colors.muted }]}>{sessions.length} saved</Text></View><View style={[styles.searchBox, { backgroundColor: colors.background, borderColor: colors.border }]}><IconSymbol name="magnifyingglass" size={16} color={colors.muted} /><TextInput value={historyQuery} onChangeText={setHistoryQuery} placeholder="Search concepts, tags, or questions" placeholderTextColor={colors.muted} style={[styles.searchInput, { color: colors.foreground }]} returnKeyType="search" /></View>{sessions.length === 0 ? <Text style={[styles.emptyHistory, { color: colors.muted }]}>Your philosophical threads will appear here after the first Oracle exchange.</Text> : filteredSessions.length === 0 ? <Text style={[styles.emptyHistory, { color: colors.muted }]}>No conversations match “{historyQuery}”. Try a concept, tag, or phrase.</Text> : <ScrollView style={styles.historyList} contentContainerStyle={styles.historyListContent}>{filteredSessions.map((session) => <View key={session.id} style={[styles.historyItem, { borderBottomColor: colors.border }]}><Pressable onPress={() => openSession(session)} style={({ pressed }) => [styles.historyOpen, pressed && styles.pressed]}><IconSymbol name="bubble.left.fill" size={16} color={colors.primary} /><View style={styles.historyCopy}><Text style={[styles.historyItemTitle, { color: colors.foreground }]} numberOfLines={1}>{session.title}</Text><Text style={[styles.historyMeta, { color: colors.muted }]}>{session.messages.filter((message) => message.role === "user").length} questions · {session.messages.reduce((count, message) => count + (message.bookmarked ? 1 : 0), 0)} saved · {new Date(session.updatedAt).toLocaleDateString()}</Text></View></Pressable><Pressable onPress={() => deleteSession(session.id)} hitSlop={8}><Text style={[styles.deleteText, { color: colors.muted }]}>×</Text></Pressable></View>)}</ScrollView>}</View> : <ScrollView contentContainerStyle={styles.chat} showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled"><View style={styles.threadBar}><Text style={[styles.threadText, { color: colors.muted }]}>{messages.length === 1 ? "NEW THREAD" : `${bookmarkedCount} SAVED INSIGHT${bookmarkedCount === 1 ? "" : "S"}`}</Text>{messages.length > 1 && <Pressable onPress={exportThread}><Text style={[styles.threadExport, { color: colors.primary }]}>Export {bookmarkedCount ? "saved" : "thread"}</Text></Pressable>}</View>{messages.map((message) => <View key={message.id} style={[styles.messageBlock, message.role === "user" && styles.userMessageBlock]}><View style={[styles.messageRow, message.role === "user" && styles.userRow]}><View style={[styles.avatar, { backgroundColor: message.role === "assistant" ? colors.primary : colors.surface, borderColor: message.role === "assistant" ? colors.primary : colors.border }]}><IconSymbol name={message.role === "assistant" ? "sparkles" : "chevron.left.forwardslash.chevron.right"} size={15} color={message.role === "assistant" ? colors.background : colors.muted} /></View><View style={[styles.bubble, { backgroundColor: message.role === "assistant" ? colors.surface : colors.primary, borderColor: message.role === "assistant" ? colors.border : colors.primary }]}><Text style={[styles.bubbleText, { color: message.role === "assistant" ? colors.foreground : colors.background }]}>{message.content}</Text></View></View>{message.id !== "welcome" && <View style={[styles.messageTools, message.role === "user" && styles.userTools]}><Pressable onPress={() => toggleBookmark(message.id)} style={({ pressed }) => [styles.toolButton, { backgroundColor: message.bookmarked ? colors.primary + "18" : colors.surface, borderColor: message.bookmarked ? colors.primary + "65" : colors.border }, pressed && styles.pressed]}><IconSymbol name="bookmark.fill" size={13} color={message.bookmarked ? colors.primary : colors.muted} /><Text style={[styles.toolText, { color: message.bookmarked ? colors.primary : colors.muted }]}>{message.bookmarked ? "Saved" : "Save"}</Text></Pressable>{message.tags.map((tag) => <Pressable key={tag} onPress={() => removeTag(message.id, tag)} style={[styles.tag, { backgroundColor: colors.primary + "12" }]}><Text style={[styles.tagText, { color: colors.primary }]}>#{tag} ×</Text></Pressable>)}<Pressable onPress={() => { setTaggingId(taggingId === message.id ? null : message.id); setTagDraft(""); }} style={({ pressed }) => [styles.tagButton, { borderColor: colors.border }, pressed && styles.pressed]}><IconSymbol name="tag.fill" size={13} color={colors.muted} /><Text style={[styles.toolText, { color: colors.muted }]}>Tag</Text></Pressable></View>}{taggingId === message.id && <View style={[styles.tagEditor, message.role === "user" && styles.userTools, { backgroundColor: colors.surface, borderColor: colors.border }]}><TextInput autoFocus value={tagDraft} onChangeText={setTagDraft} onSubmitEditing={() => addTag(message.id)} placeholder="Add a tag, e.g. monads" placeholderTextColor={colors.muted} style={[styles.tagInput, { color: colors.foreground }]} maxLength={24} returnKeyType="done" /><Pressable onPress={() => addTag(message.id)}><Text style={[styles.addTagText, { color: colors.primary }]}>Add</Text></Pressable></View>}</View>)}{chat.isPending && <View style={styles.messageRow}><View style={[styles.avatar, { backgroundColor: colors.primary, borderColor: colors.primary }]}><IconSymbol name="sparkles" size={15} color={colors.background} /></View><View style={[styles.bubble, { backgroundColor: colors.surface, borderColor: colors.border }]}><ActivityIndicator color={colors.primary} size="small" /></View></View>}{messages.length === 1 && <View style={styles.promptWrap}>{starterPrompts.map(prompt => <Pressable key={prompt} onPress={() => send(prompt)} style={({ pressed }) => [styles.prompt, { borderColor: colors.border, backgroundColor: colors.surface }, pressed && styles.pressed]}><Text style={[styles.promptText, { color: colors.foreground }]}>{prompt}</Text><IconSymbol name="chevron.right" size={15} color={colors.primary} /></Pressable>)}</View>}{followUps.length > 0 && !chat.isPending && messages.length > 1 && <View style={styles.followUpWrap}><Text style={[styles.followUpLabel, { color: colors.muted }]}>CONTINUE THIS THREAD</Text>{followUps.map((followUp) => <Pressable key={followUp} onPress={() => send(followUp)} style={({ pressed }) => [styles.followUp, { backgroundColor: colors.primary + "12", borderColor: colors.primary + "45" }, pressed && styles.pressed]}><Text style={[styles.followUpText, { color: colors.foreground }]}>{followUp}</Text><IconSymbol name="chevron.right" size={14} color={colors.primary} /></Pressable>)}</View>}</ScrollView>}

    <View style={[styles.composer, { backgroundColor: colors.surface, borderColor: colors.border }]}><TextInput value={draft} onChangeText={setDraft} onSubmitEditing={() => send()} returnKeyType="send" placeholder="Ask about a file, idea, or proof..." placeholderTextColor={colors.muted} multiline maxLength={500} style={[styles.input, { color: colors.foreground }]} /><Pressable disabled={!canSend} onPress={() => send()} style={({ pressed }) => [styles.sendButton, { backgroundColor: canSend ? colors.primary : colors.border }, pressed && styles.pressed]}><IconSymbol name="chevron.right" size={19} color={canSend ? colors.background : colors.muted} /></Pressable></View>
    <Text style={[styles.disclaimer, { color: colors.muted }]}>The Oracle explains the repository; it does not replace Lean's kernel or the repo's measurement scripts.</Text>
  </KeyboardAvoidingView></ScreenContainer>;
}

const styles = StyleSheet.create({
  flex: { flex: 1 }, header: { paddingHorizontal: 22, paddingTop: 5, flexDirection: "row", alignItems: "flex-end", justifyContent: "space-between" }, eyebrow: { fontSize: 10, letterSpacing: 1.6, fontWeight: "800" }, title: { fontSize: 29, fontWeight: "800", letterSpacing: -0.7, marginTop: 4 }, headerActions: { flexDirection: "row", gap: 6, alignItems: "center" }, headerButton: { minHeight: 30, borderWidth: 1, borderRadius: 15, paddingHorizontal: 8, flexDirection: "row", alignItems: "center", gap: 4 }, headerButtonText: { fontSize: 10, fontWeight: "900" }, newText: { fontSize: 10, fontWeight: "900" }, statusRow: { paddingHorizontal: 22, flexDirection: "row", alignItems: "flex-end", justifyContent: "space-between", gap: 10 }, subtitle: { flex: 1, fontSize: 13, lineHeight: 19, marginTop: 7 }, online: { flexDirection: "row", alignItems: "center", gap: 6, borderWidth: 1, borderRadius: 20, paddingHorizontal: 9, paddingVertical: 6, marginBottom: 2 }, onlineDot: { width: 6, height: 6, borderRadius: 3 }, onlineText: { fontSize: 9, letterSpacing: 1, fontWeight: "900" }, interpretation: { marginHorizontal: 22, marginTop: 10, paddingHorizontal: 10, paddingVertical: 7, borderWidth: 1, borderRadius: 10, flexDirection: "row", alignItems: "center", gap: 6, alignSelf: "flex-start" }, interpretationText: { fontSize: 10, fontWeight: "800", letterSpacing: 0.3 }, historyPanel: { margin: 18, marginBottom: 4, borderWidth: 1, borderRadius: 17, padding: 14, flex: 1 }, historyTitleRow: { flexDirection: "row", alignItems: "flex-end", justifyContent: "space-between", marginBottom: 8 }, historyEyebrow: { fontSize: 9, letterSpacing: 1.6, fontWeight: "900" }, historyTitle: { fontSize: 18, fontWeight: "800", marginTop: 3 }, historyCount: { fontSize: 10 }, searchBox: { minHeight: 39, borderRadius: 11, borderWidth: 1, flexDirection: "row", alignItems: "center", paddingHorizontal: 10, gap: 7, marginBottom: 6 }, searchInput: { flex: 1, fontSize: 12, paddingVertical: 7 }, historyList: { flex: 1 }, historyListContent: { gap: 2 }, emptyHistory: { fontSize: 12, lineHeight: 18, paddingVertical: 14 }, historyItem: { minHeight: 58, borderBottomWidth: 1, flexDirection: "row", alignItems: "center", justifyContent: "space-between" }, historyOpen: { flex: 1, flexDirection: "row", alignItems: "center", gap: 10 }, historyCopy: { flex: 1 }, historyItemTitle: { fontSize: 13, fontWeight: "800" }, historyMeta: { fontSize: 10, marginTop: 3 }, deleteText: { fontSize: 21, paddingHorizontal: 6 }, chat: { paddingHorizontal: 22, paddingTop: 13, paddingBottom: 14, gap: 12 }, threadBar: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 2 }, threadText: { fontSize: 9, letterSpacing: 1.5, fontWeight: "900" }, threadExport: { fontSize: 10, fontWeight: "900" }, messageBlock: { gap: 5 }, userMessageBlock: { alignItems: "flex-end" }, messageRow: { flexDirection: "row", alignItems: "flex-start", gap: 8, maxWidth: "92%" }, userRow: { alignSelf: "flex-end", flexDirection: "row-reverse" }, avatar: { width: 27, height: 27, borderRadius: 14, borderWidth: 1, alignItems: "center", justifyContent: "center" }, bubble: { borderRadius: 16, borderWidth: 1, padding: 12, flexShrink: 1 }, bubbleText: { fontSize: 13, lineHeight: 19 }, messageTools: { marginLeft: 35, flexDirection: "row", alignItems: "center", gap: 5, flexWrap: "wrap" }, userTools: { marginLeft: 0, marginRight: 35, justifyContent: "flex-end" }, toolButton: { borderWidth: 1, borderRadius: 9, paddingHorizontal: 7, paddingVertical: 5, flexDirection: "row", alignItems: "center", gap: 4 }, toolText: { fontSize: 9, fontWeight: "800" }, tagButton: { borderWidth: 1, borderRadius: 9, paddingHorizontal: 7, paddingVertical: 5, flexDirection: "row", alignItems: "center", gap: 4 }, tag: { borderRadius: 8, paddingHorizontal: 7, paddingVertical: 5 }, tagText: { fontSize: 9, fontWeight: "800" }, tagEditor: { marginLeft: 35, borderWidth: 1, borderRadius: 10, paddingHorizontal: 8, paddingVertical: 4, flexDirection: "row", alignItems: "center", maxWidth: "78%" }, tagInput: { flex: 1, fontSize: 11, paddingVertical: 4 }, addTagText: { fontSize: 10, fontWeight: "900", paddingHorizontal: 6 }, promptWrap: { gap: 8, marginTop: 5 }, prompt: { borderWidth: 1, borderRadius: 12, paddingHorizontal: 12, paddingVertical: 10, flexDirection: "row", alignItems: "center", justifyContent: "space-between" }, promptText: { fontSize: 12, fontWeight: "700", flex: 1 }, followUpWrap: { gap: 7, marginTop: 4 }, followUpLabel: { fontSize: 9, letterSpacing: 1.3, fontWeight: "900", marginBottom: 1 }, followUp: { borderWidth: 1, borderRadius: 12, paddingHorizontal: 11, paddingVertical: 9, flexDirection: "row", alignItems: "center", justifyContent: "space-between" }, followUpText: { fontSize: 12, fontWeight: "700", flex: 1, paddingRight: 8 }, pressed: { opacity: 0.7, transform: [{ scale: 0.985 }] }, composer: { marginHorizontal: 18, minHeight: 54, maxHeight: 112, borderWidth: 1, borderRadius: 17, flexDirection: "row", alignItems: "center", paddingLeft: 14, paddingRight: 7, paddingVertical: 6, gap: 8 }, input: { flex: 1, fontSize: 13, lineHeight: 18, paddingVertical: 6, maxHeight: 90 }, sendButton: { width: 39, height: 39, borderRadius: 13, alignItems: "center", justifyContent: "center" }, disclaimer: { fontSize: 10, lineHeight: 14, textAlign: "center", paddingHorizontal: 25, paddingVertical: 8 },
});
