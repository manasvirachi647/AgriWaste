import React from "react";
import { Stack } from "expo-router";
import { Colors } from "../constants/colors";

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: Colors.primary,
        },
        headerTintColor: Colors.white,
        headerTitleStyle: {
          fontWeight: "700",
        },
        contentStyle: {
          backgroundColor: Colors.background,
        },
      }}
    >
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="(auth)/select-role" options={{ title: "Select Role" }} />
      <Stack.Screen name="(auth)/login" options={{ title: "Sign In" }} />
      <Stack.Screen name="(auth)/register" options={{ title: "Create Account" }} />
      <Stack.Screen name="(farmer)/dashboard" options={{ title: "Farmer Dashboard", headerShown: false }} />
      <Stack.Screen name="(buyer)/dashboard" options={{ title: "Buyer Dashboard", headerShown: false }} />
      <Stack.Screen name="(aggregator)/dashboard" options={{ title: "Transporter Dashboard", headerShown: false }} />
      <Stack.Screen name="(admin)/dashboard" options={{ title: "Admin Portal", headerShown: false }} />
    </Stack>
  );
}
