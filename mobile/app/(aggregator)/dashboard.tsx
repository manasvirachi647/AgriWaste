import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  RefreshControl,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "../../constants/colors";
import { Header } from "../../components/Header";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { authService, UserProfile } from "../../services/auth";

export default function AggregatorDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(authService.getCachedUser());
  const [refreshing, setRefreshing] = useState(false);

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
        title={user?.full_name || "Transporter"}
        subtitle={user?.aggregator_profile?.vehicle_type || "Rural Aggregation & Logistics"}
        badge="TRANSPORTER"
      />

      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.statsRow}>
          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>0</Text>
            <Text style={styles.statLabel}>Active Trips</Text>
          </Card>

          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>0</Text>
            <Text style={styles.statLabel}>Completed</Text>
          </Card>
        </View>

        <View style={styles.sectionHeaderRow}>
          <Text style={styles.sectionTitle}>Assigned Collection & Delivery Jobs</Text>
        </View>

        <Card style={styles.emptyCard}>
          <Text style={styles.emptyEmoji}>🚛</Text>
          <Text style={styles.emptyTitle}>No active transport assignments</Text>
          <Text style={styles.emptySubtitle}>
            When a buyer order with multi-farmer pickups is confirmed, pickup locations and routing instructions will appear here.
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
    color: Colors.accent,
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
  emptyCard: {
    alignItems: "center",
    paddingVertical: 30,
    marginVertical: 8,
  },
  emptyEmoji: {
    fontSize: 40,
    marginBottom: 10,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  emptySubtitle: {
    fontSize: 13,
    color: Colors.textSecondary,
    textAlign: "center",
    paddingHorizontal: 20,
    marginTop: 6,
    lineHeight: 18,
  },
  logoutContainer: {
    marginTop: 24,
    marginBottom: 20,
  },
});
