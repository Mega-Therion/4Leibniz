import { Tabs } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Platform } from "react-native";

import { HapticTab } from "@/components/haptic-tab";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { useColors } from "@/hooks/use-colors";

export default function TabLayout() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const bottomPadding = Platform.OS === "web" ? 10 : Math.max(insets.bottom, 8);
  const tabBarHeight = 58 + bottomPadding;

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.tint,
        tabBarInactiveTintColor: colors.muted,
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarStyle: {
          paddingTop: 8,
          paddingBottom: bottomPadding,
          height: tabBarHeight,
          backgroundColor: colors.background,
          borderTopColor: colors.border,
          borderTopWidth: 0.5,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: "600" },
      }}
    >
      <Tabs.Screen name="index" options={{ title: "Home", tabBarIcon: ({ color }) => <IconSymbol size={23} name="house.fill" color={color} /> }} />
      <Tabs.Screen name="learn" options={{ title: "Learn", tabBarIcon: ({ color }) => <IconSymbol size={23} name="book.fill" color={color} /> }} />
      <Tabs.Screen name="lab" options={{ title: "Lab", tabBarIcon: ({ color }) => <IconSymbol size={23} name="flask.fill" color={color} /> }} />
      <Tabs.Screen name="guide" options={{ title: "Guide", tabBarIcon: ({ color }) => <IconSymbol size={23} name="bubble.left.fill" color={color} /> }} />
      <Tabs.Screen name="saved" options={{ title: "Saved", tabBarIcon: ({ color }) => <IconSymbol size={23} name="bookmark.fill" color={color} /> }} />
    </Tabs>
  );
}
