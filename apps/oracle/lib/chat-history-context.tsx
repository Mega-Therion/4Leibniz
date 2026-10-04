import AsyncStorage from "@react-native-async-storage/async-storage";
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/hooks/use-auth";

export type InsightTopic = "Monadology" | "Calculus" | "Epistemology" | "Physics" | "Repository";
export const insightTopics: InsightTopic[] = ["Monadology", "Calculus", "Epistemology", "Physics", "Repository"];
export type ChatMessage = { id: string; role: "user" | "assistant"; content: string; bookmarked: boolean; tags: string[]; topic: InsightTopic };
export type ChatProfile = { domain: string; task: string; difficulty: string };
export type ChatSession = { id: string; title: string; messages: ChatMessage[]; profile: ChatProfile | null; updatedAt: number };

type ChatHistoryValue = {
  sessions: ChatSession[];
  hydrated: boolean;
  cloudEnabled: boolean;
  cloudSyncing: boolean;
  saveSession: (session: ChatSession) => void;
  deleteSession: (id: string) => void;
  updateMessage: (sessionId: string, messageId: string, updater: (message: ChatMessage) => ChatMessage) => void;
};

const STORAGE_KEY = "leibniz-oracle.chat-history.v1";
const ChatHistoryContext = createContext<ChatHistoryValue | null>(null);

export function inferTopic(content: string, profile?: ChatProfile | null): InsightTopic {
  const normalized = `${content} ${profile?.domain ?? ""}`.toLowerCase();
  if (/monad|monadology|substance|perception|appetition/.test(normalized)) return "Monadology";
  if (/calculus|characteristica|logic|symbol|formal|proof|theorem|lean/.test(normalized)) return "Calculus";
  if (/knowledge|evidence|reason|epistem|truth|certainty|interpret/.test(normalized)) return "Epistemology";
  if (/physics|force|motion|vis viva|harmonia|coherence|space|relativ/.test(normalized)) return "Physics";
  return "Repository";
}

function migrateSession(session: Partial<ChatSession>, index: number): ChatSession | null {
  if (!session.id || !Array.isArray(session.messages)) return null;
  const profile = session.profile ?? null;
  return {
    id: session.id,
    title: session.title || "Untitled reflection",
    profile,
    updatedAt: typeof session.updatedAt === "number" ? session.updatedAt : Date.now() - index,
    messages: session.messages.filter(Boolean).map((message, messageIndex) => ({
      id: message.id || `${session.id}-${messageIndex}`,
      role: message.role === "user" ? "user" : "assistant",
      content: message.content || "",
      bookmarked: Boolean(message.bookmarked),
      tags: Array.isArray(message.tags) ? message.tags.map(String).slice(0, 6) : [],
      topic: insightTopics.includes(message.topic as InsightTopic) ? message.topic as InsightTopic : inferTopic(message.content || "", profile),
    })),
  };
}

function parseSessions(payload: string | null | undefined) {
  if (!payload) return [] as ChatSession[];
  try {
    const parsed = JSON.parse(payload) as Partial<ChatSession>[];
    return Array.isArray(parsed) ? parsed.map(migrateSession).filter((session): session is ChatSession => Boolean(session)).slice(0, 20) : [];
  } catch {
    return [] as ChatSession[];
  }
}

function mergeSessions(local: ChatSession[], remote: ChatSession[]) {
  const merged = new Map<string, ChatSession>();
  [...remote, ...local].forEach((session) => {
    const current = merged.get(session.id);
    if (!current || session.updatedAt >= current.updatedAt) merged.set(session.id, session);
  });
  return Array.from(merged.values()).sort((a, b) => b.updatedAt - a.updatedAt).slice(0, 20);
}

export function ChatHistoryProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const [cloudReady, setCloudReady] = useState(false);
  const { isAuthenticated, loading: authLoading } = useAuth();
  const cloudPull = trpc.insights.pull.useQuery(undefined, { enabled: isAuthenticated });
  const cloudPush = trpc.insights.push.useMutation();

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((raw) => {
      setSessions(parseSessions(raw));
      setHydrated(true);
    });
  }, []);

  useEffect(() => {
    if (hydrated) void AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(sessions.slice(0, 20)));
  }, [hydrated, sessions]);

  useEffect(() => {
    if (!hydrated || authLoading) return;
    if (!isAuthenticated) setCloudReady(true);
  }, [authLoading, hydrated, isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated || !cloudPull.isSuccess || !hydrated) return;
    const remoteSessions = parseSessions(cloudPull.data.payload);
    if (remoteSessions.length > 0) setSessions((current) => mergeSessions(current, remoteSessions));
    setCloudReady(true);
  }, [cloudPull.data, cloudPull.isSuccess, hydrated, isAuthenticated]);

  useEffect(() => {
    if (!cloudReady || !isAuthenticated || !hydrated || sessions.length === 0) return;
    cloudPush.mutate({ payload: JSON.stringify(sessions.slice(0, 20)) });
  }, [cloudReady, hydrated, isAuthenticated, sessions]);

  const value = useMemo(() => ({
    sessions,
    hydrated,
    cloudEnabled: isAuthenticated,
    cloudSyncing: cloudPush.isPending || (isAuthenticated && !cloudReady),
    saveSession: (session: ChatSession) => setSessions((current) => [session, ...current.filter((item) => item.id !== session.id)].sort((a, b) => b.updatedAt - a.updatedAt).slice(0, 20)),
    deleteSession: (id: string) => setSessions((current) => current.filter((session) => session.id !== id)),
    updateMessage: (sessionId: string, messageId: string, updater: (message: ChatMessage) => ChatMessage) => setSessions((current) => current.map((session) => session.id !== sessionId ? session : { ...session, updatedAt: Date.now(), messages: session.messages.map((message) => message.id === messageId ? updater(message) : message) })),
  }), [cloudPush.isPending, cloudReady, hydrated, isAuthenticated, sessions]);

  return <ChatHistoryContext.Provider value={value}>{children}</ChatHistoryContext.Provider>;
}

export function useChatHistory() {
  const context = useContext(ChatHistoryContext);
  if (!context) throw new Error("useChatHistory must be used inside ChatHistoryProvider");
  return context;
}
