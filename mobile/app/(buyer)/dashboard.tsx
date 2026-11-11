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
import { api } from "../../services/api";

interface AvailableListing {
  id: number;
  material_name: string;
  available_quantity: number;
  unit: string;
  price_per_unit: number;
  location_name: string;
  storage_type?: string;
}

export default function BuyerDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(authService.getCachedUser());
  const [availableListings, setAvailableListings] = useState<AvailableListing[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const me = await authService.getCurrentUser();
      setUser(me);
      const res = await api.get<AvailableListing[]>("/listings");
      setAvailableListings(res.data);
    } catch (err) {
      console.log("Error loading buyer data:", err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleLogout = () => {
    authService.logout();
    router.replace("/");
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header
        title={user?.buyer_profile?.company_name || user?.full_name || "Industrial Buyer"}
        subtitle={user?.buyer_profile?.industry_type || "Biomass Procurement Portal"}
        badge="BUYER"
      />

      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Quick Stats Grid */}
        <View style={styles.statsRow}>
          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>0</Text>
            <Text style={styles.statLabel}>Active Demands</Text>
          </Card>

          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>{availableListings.length}</Text>
            <Text style={styles.statLabel}>Farm Supplies</Text>
          </Card>
        </View>

        {/* Action Button */}
        <Button
          title="+ Publish Biomass Requirement"
          onPress={() => {
            alert("Week 4 Feature: Post Requirement Form connecting to POST /requirements");
          }}
          variant="secondary"
          style={styles.addBtn}
        />

        {/* Live Marketplace Feed */}
        <View style={styles.sectionHeaderRow}>
          <Text style={styles.sectionTitle}>Available Farm Residue Supply</Text>
          <Text style={styles.countText}>{availableListings.length} suppliers</Text>
        </View>

        {availableListings.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyEmoji}>🏭</Text>
            <Text style={styles.emptyTitle}>No farm supplies listed right now</Text>
            <Text style={styles.emptySubtitle}>
              Farmers will list seasonal harvest residue here. You can publish a requirement to broadcast your demand.
            </Text>
          </Card>
        ) : (
          availableListings.map((item) => (
            <Card key={item.id} style={styles.listingCard}>
              <View style={styles.listingTop}>
                <Text style={styles.listingMaterial}>{item.material_name}</Text>
                <Text style={styles.priceTag}>₹{item.price_per_unit}/{item.unit}</Text>
              </View>

              <Text style={styles.listingDetails}>
                Available: <Text style={styles.bold}>{item.available_quantity} {item.unit}</Text>
              </Text>
              <Text style={styles.listingLocation}>📍 {item.location_name}</Text>
              {item.storage_type && (
                <Text style={styles.storageNote}>📦 Storage: {item.storage_type}</Text>
              )}
            </Card>
          ))
        )}

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
    color: Colors.secondary,
  },
  statLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 4,
    fontWeight: "500",
  },
  addBtn: {
    marginVertical: 10,
  },
  sectionHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  countText: {
    fontSize: 13,
    color: Colors.textSecondary,
  },
  listingCard: {
    marginVertical: 6,
  },
  listingTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  listingMaterial: {
    fontSize: 17,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  priceTag: {
    fontSize: 16,
    fontWeight: "800",
    color: Colors.primaryDark,
  },
  listingDetails: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 6,
  },
  bold: {
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  listingLocation: {
    fontSize: 13,
    color: Colors.textMuted,
    marginTop: 4,
  },
  storageNote: {
    fontSize: 12,
    color: Colors.accent,
    marginTop: 4,
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
