import AsyncStorage from "@react-native-async-storage/async-storage";
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { lessons } from "@/lib/leibniz-data";

const STORAGE_KEY = "leibniz-oracle.progress.v1";

type PersistedProgress = {
  bookmarkedLessons: string[];
  completedLessons: string[];
};

type ProgressContextValue = PersistedProgress & {
  hydrated: boolean;
  toggleBookmark: (lessonId: string) => void;
  toggleComplete: (lessonId: string) => void;
  isBookmarked: (lessonId: string) => boolean;
  isComplete: (lessonId: string) => boolean;
  completedCount: number;
  bookmarkedCount: number;
  progressPercent: number;
  nextMilestone: { label: string; threshold: number } | null;
};

const ProgressContext = createContext<ProgressContextValue | null>(null);

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<PersistedProgress>({ bookmarkedLessons: [], completedLessons: [] });
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((raw) => {
      if (raw) {
        try {
          const parsed = JSON.parse(raw) as PersistedProgress;
          setState({
            bookmarkedLessons: Array.isArray(parsed.bookmarkedLessons) ? parsed.bookmarkedLessons : [],
            completedLessons: Array.isArray(parsed.completedLessons) ? parsed.completedLessons : [],
          });
        } catch {
          // Keep the empty state if an old or corrupted local value is found.
        }
      }
      setHydrated(true);
    });
  }, []);

  useEffect(() => {
    if (hydrated) void AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [hydrated, state]);

  const value = useMemo<ProgressContextValue>(() => {
    const completedCount = state.completedLessons.length;
    const bookmarkedCount = state.bookmarkedLessons.length;
    const progressPercent = lessons.length === 0 ? 0 : Math.round((completedCount / lessons.length) * 100);
    const milestones = [
      { label: "First annotation", threshold: 1 },
      { label: "A three-part thinker", threshold: 3 },
      { label: "Library complete", threshold: lessons.length },
    ];
    const nextMilestone = milestones.find((milestone) => completedCount < milestone.threshold) ?? null;

    return {
      ...state,
      hydrated,
      toggleBookmark: (lessonId) => setState((current) => ({
        ...current,
        bookmarkedLessons: current.bookmarkedLessons.includes(lessonId)
          ? current.bookmarkedLessons.filter((id) => id !== lessonId)
          : [...current.bookmarkedLessons, lessonId],
      })),
      toggleComplete: (lessonId) => setState((current) => ({
        ...current,
        completedLessons: current.completedLessons.includes(lessonId)
          ? current.completedLessons.filter((id) => id !== lessonId)
          : [...current.completedLessons, lessonId],
      })),
      isBookmarked: (lessonId) => state.bookmarkedLessons.includes(lessonId),
      isComplete: (lessonId) => state.completedLessons.includes(lessonId),
      completedCount,
      bookmarkedCount,
      progressPercent,
      nextMilestone,
    };
  }, [hydrated, state]);

  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>;
}

export function useProgress() {
  const context = useContext(ProgressContext);
  if (!context) throw new Error("useProgress must be used inside ProgressProvider");
  return context;
}
