import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "../../constants/colors";
import { Header } from "../../components/Header";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { authService, UserProfile } from "../../services/auth";

export default function AdminDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(authService.getCachedUser());

  useEffect(() => {
    authService.getCurrentUser().then(setUser).catch(() => {});
  }, []);

  const handleLogout = () => {
    authService.logout();
    router.replace("/");
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header
        title={user?.full_name || "Platform Admin"}
        subtitle="AgriWaste Exchange Administration Portal"
        badge="ADMIN"
      />

      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.statsRow}>
          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>100%</Text>
            <Text style={styles.statLabel}>API Health</Text>
          </Card>

          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>Active</Text>
            <Text style={styles.statLabel}>DB Status</Text>
          </Card>
        </View>

        <View style={styles.sectionHeaderRow}>
          <Text style={styles.sectionTitle}>Marketplace Moderation</Text>
        </View>

        <Card>
          <Text style={styles.itemTitle}>👥 User Management</Text>
          <Text style={styles.itemDescription}>
            Manage registered farmers, industrial buyers, and verified aggregators.
          </Text>
        </Card>

        <Card>
          <Text style={styles.itemTitle}>⚖️ Issue Reports & Dispute Tracking</Text>
          <Text style={styles.itemDescription}>
            Audit reported quality discrepancies or transport delay tickets.
          </Text>
        </Card>

        <View style={styles.logoutContainer}>
          <Button title="Sign Out" onPress={handleLogout} variant="outline" />
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
    padding: 16,
  },
  statsRow: {
    flexDirection: "row",
    gap: 12,
  },
  statCard: {
    flex: 1,
    alignItems: "center",
    paddingVertical: 18,
  },
  statNumber: {
    fontSize: 22,
    fontWeight: "800",
    color: Colors.primaryDark,
  },
  statLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 4,
    fontWeight: "500",
  },
  sectionHeaderRow: {
    marginTop: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  itemDescription: {
    fontSize: 13,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
  logoutContainer: {
    marginTop: 24,
    marginBottom: 20,
  },
});
