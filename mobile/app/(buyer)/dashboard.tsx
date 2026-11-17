import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  RefreshControl,
  TouchableOpacity,
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

interface BuyerRequirementItem {
  id: number;
  material_name: string;
  required_quantity: number;
  fulfilled_quantity: number;
  unit: string;
  delivery_location: string;
  target_price_max?: number;
  status: string;
}

export default function BuyerDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(authService.getCachedUser());
  const [myRequirements, setMyRequirements] = useState<BuyerRequirementItem[]>([]);
  const [availableListings, setAvailableListings] = useState<AvailableListing[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const me = await authService.getCurrentUser();
      setUser(me);

      // Load buyer's published requirements
      const reqRes = await api.get<BuyerRequirementItem[]>("/requirements/my");
      setMyRequirements(reqRes.data);

      // Load public farm listings
      const listRes = await api.get<AvailableListing[]>("/listings");
      setAvailableListings(listRes.data);
    } catch (err) {
      console.log("Error loading buyer dashboard data:", err);
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

  const totalDemandTonnes = myRequirements.reduce(
    (sum, r) => sum + (r.required_quantity || 0),
    0
  );

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
            <Text style={styles.statNumber}>{myRequirements.length}</Text>
            <Text style={styles.statLabel}>Active Demands</Text>
          </Card>

          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>{totalDemandTonnes.toFixed(1)} T</Text>
            <Text style={styles.statLabel}>Total Demand</Text>
          </Card>

          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>{availableListings.length}</Text>
            <Text style={styles.statLabel}>Farm Supplies</Text>
          </Card>
        </View>

        {/* Action Button */}
        <Button
          title="+ Publish Biomass Requirement"
          onPress={() => router.push("/(buyer)/requirements/add")}
          variant="secondary"
          style={styles.addBtn}
        />

        {/* My Published Requirements Section */}
        <View style={styles.sectionHeaderRow}>
          <Text style={styles.sectionTitle}>My Published Demands</Text>
          <TouchableOpacity onPress={() => router.push("/(buyer)/requirements/index")}>
            <Text style={styles.viewAllText}>View All ({myRequirements.length}) →</Text>
          </TouchableOpacity>
        </View>

        {myRequirements.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyEmoji}>📋</Text>
            <Text style={styles.emptyTitle}>No requirements posted yet</Text>
            <Text style={styles.emptySubtitle}>
              Publish your biomass demand to let nearby farmers and aggregators know your facility's raw material needs.
            </Text>
          </Card>
        ) : (
          myRequirements.map((req) => (
            <TouchableOpacity
              key={req.id}
              activeOpacity={0.8}
              onPress={() => router.push(`/(buyer)/requirements/${req.id}`)}
            >
              <Card style={styles.reqCard}>
                <View style={styles.reqTop}>
                  <Text style={styles.reqMaterial}>{req.material_name}</Text>
                  <View style={styles.statusBadge}>
                    <Text style={styles.statusText}>{req.status.toUpperCase()}</Text>
                  </View>
                </View>

                <Text style={styles.reqDetails}>
                  Demanded: <Text style={styles.bold}>{req.required_quantity} {req.unit}</Text>
                  {req.target_price_max ? ` • Max Rate: ₹${req.target_price_max}/${req.unit}` : ""}
                </Text>
                <Text style={styles.reqLocation}>📍 Delivery to: {req.delivery_location}</Text>
                <Text style={styles.tapPrompt}>Tap to see details & matching farmer suppliers →</Text>
              </Card>
            </TouchableOpacity>
          ))
        )}

        {/* Live Marketplace Supply Feed */}
        <View style={[styles.sectionHeaderRow, { marginTop: 20 }]}>
          <Text style={styles.sectionTitle}>Marketplace Farm Supply Feed</Text>
          <Text style={styles.countText}>{availableListings.length} suppliers</Text>
        </View>

        {availableListings.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyEmoji}>🌾</Text>
            <Text style={styles.emptyTitle}>No farm supplies listed right now</Text>
            <Text style={styles.emptySubtitle}>
              Farmers will list seasonal harvest residue here.
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
              {item.storage_type ? (
                <Text style={styles.storageNote}>📦 Storage: {item.storage_type}</Text>
              ) : null}
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
    gap: 8,
  },
  statCard: {
    flex: 1,
    alignItems: "center",
    paddingVertical: 14,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: "800",
    color: Colors.secondary,
  },
  statLabel: {
    fontSize: 11,
    color: Colors.textSecondary,
    marginTop: 4,
    fontWeight: "600",
  },
  addBtn: {
    marginVertical: 10,
  },
  sectionHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 14,
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
  viewAllText: {
    fontSize: 13,
    color: Colors.secondary,
    fontWeight: "700",
  },
  reqCard: {
    marginVertical: 6,
    borderLeftWidth: 4,
    borderLeftColor: Colors.secondary,
  },
  reqTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  reqMaterial: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  statusBadge: {
    backgroundColor: Colors.secondaryLight,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  statusText: {
    color: Colors.secondary,
    fontSize: 11,
    fontWeight: "700",
  },
  reqDetails: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 6,
  },
  reqLocation: {
    fontSize: 13,
    color: Colors.textMuted,
    marginTop: 4,
  },
  tapPrompt: {
    fontSize: 11,
    color: Colors.secondary,
    fontWeight: "600",
    marginTop: 8,
  },
  listingCard: {
    marginVertical: 6,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  listingTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  listingMaterial: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  priceTag: {
    fontSize: 15,
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
    paddingVertical: 24,
    marginVertical: 6,
  },
  emptyEmoji: {
    fontSize: 36,
    marginBottom: 8,
  },
  emptyTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  emptySubtitle: {
    fontSize: 13,
    color: Colors.textSecondary,
    textAlign: "center",
    paddingHorizontal: 20,
    marginTop: 4,
    lineHeight: 18,
  },
  logoutContainer: {
    marginTop: 24,
    marginBottom: 20,
  },
});
