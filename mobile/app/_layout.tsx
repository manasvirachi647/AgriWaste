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
      <Stack.Screen name="(farmer)/listings/index" options={{ title: "My Listings", headerShown: false }} />
      <Stack.Screen name="(farmer)/listings/add" options={{ title: "Add Crop Residue", headerShown: false }} />
      <Stack.Screen name="(farmer)/listings/[id]" options={{ title: "Listing Details", headerShown: false }} />
      <Stack.Screen name="(buyer)/dashboard" options={{ title: "Buyer Dashboard", headerShown: false }} />
      <Stack.Screen name="(buyer)/requirements/index" options={{ title: "My Requirements", headerShown: false }} />
      <Stack.Screen name="(buyer)/requirements/add" options={{ title: "Publish Requirement", headerShown: false }} />
      <Stack.Screen name="(buyer)/requirements/[id]" options={{ title: "Requirement Details", headerShown: false }} />
      <Stack.Screen name="(aggregator)/dashboard" options={{ title: "Transporter Dashboard", headerShown: false }} />
      <Stack.Screen name="(admin)/dashboard" options={{ title: "Admin Portal", headerShown: false }} />
    </Stack>
  );
}
