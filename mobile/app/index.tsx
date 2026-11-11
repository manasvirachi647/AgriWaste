import React from "react";
import { View, Text, StyleSheet, SafeAreaView, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "../constants/colors";
import { Button } from "../components/Button";
import { Card } from "../components/Card";

export default function WelcomeScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Hero Section */}
        <View style={styles.heroSection}>
          <View style={styles.iconCircle}>
            <Text style={styles.heroIcon}>🌾</Text>
          </View>
          <Text style={styles.appTitle}>AgriWaste Exchange</Text>
          <Text style={styles.tagline}>
            Transforming Agricultural Residue into Industrial Value
          </Text>
        </View>

        {/* Value Proposition Cards */}
        <View style={styles.featuresContainer}>
          <Card style={styles.featureCard}>
            <Text style={styles.featureEmoji}>👨‍🌾 For Farmers</Text>
            <Text style={styles.featureText}>
              Fair compensation for surplus crop residue like rice husk, wheat straw & bagasse. Reduce stubble burning.
            </Text>
          </Card>

          <Card style={styles.featureCard}>
            <Text style={styles.featureEmoji}>🏭 For Industrial Buyers</Text>
            <Text style={styles.featureText}>
              Dependable bulk biomass supply through automated multi-farmer aggregation and verifiable quality.
            </Text>
          </Card>

          <Card style={styles.featureCard}>
            <Text style={styles.featureEmoji}>🚛 For Transporters</Text>
            <Text style={styles.featureText}>
              Optimized rural pickup jobs connecting farms directly with biomass processing facilities.
            </Text>
          </Card>
        </View>

        {/* Soil Health Advisory Badge */}
        <View style={styles.advisoryBanner}>
          <Text style={styles.advisoryTitle}>🌱 Sustainable Residue Management</Text>
          <Text style={styles.advisoryText}>
            Sell only what is surplus! Always retain the required residue for soil health, livestock feed, and local composting.
          </Text>
        </View>

        {/* CTA Buttons */}
        <View style={styles.buttonGroup}>
          <Button
            title="Get Started / Register"
            onPress={() => router.push("/(auth)/select-role")}
            variant="primary"
          />
          <Button
            title="Already have an account? Sign In"
            onPress={() => router.push("/(auth)/login")}
            variant="outline"
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  container: {
    padding: 24,
    justifyContent: "center",
  },
  heroSection: {
    alignItems: "center",
    marginVertical: 20,
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: Colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
  },
  heroIcon: {
    fontSize: 40,
  },
  appTitle: {
    fontSize: 28,
    fontWeight: "800",
    color: Colors.primaryDark,
    textAlign: "center",
  },
  tagline: {
    fontSize: 15,
    color: Colors.textSecondary,
    textAlign: "center",
    marginTop: 8,
    paddingHorizontal: 20,
    lineHeight: 22,
  },
  featuresContainer: {
    marginVertical: 12,
  },
  featureCard: {
    marginVertical: 6,
    padding: 14,
  },
  featureEmoji: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.primary,
    marginBottom: 4,
  },
  featureText: {
    fontSize: 13,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
  advisoryBanner: {
    backgroundColor: Colors.successLight,
    borderColor: Colors.success,
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginVertical: 12,
  },
  advisoryTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.primaryDark,
    marginBottom: 4,
  },
  advisoryText: {
    fontSize: 12,
    color: Colors.textSecondary,
    lineHeight: 16,
  },
  buttonGroup: {
    marginTop: 16,
  },
});
