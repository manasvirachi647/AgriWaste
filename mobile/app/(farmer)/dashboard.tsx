import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  TouchableOpacity,
  RefreshControl,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "../../constants/colors";
import { Header } from "../../components/Header";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { authService, UserProfile } from "../../services/auth";
import { api } from "../../services/api";

interface ListingItem {
  id: number;
  material_name: string;
  available_quantity: number;
  unit: string;
  price_per_unit: number;
  location_name: string;
  status: string;
}

export default function FarmerDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(authService.getCachedUser());
  const [listings, setListings] = useState<ListingItem[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const me = await authService.getCurrentUser();
      setUser(me);
      const res = await api.get<ListingItem[]>("/listings/my");
      setListings(res.data);
    } catch (err) {
      console.log("Error loading farmer data:", err);
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

  const totalQuantity = listings.reduce((sum, item) => sum + (item.available_quantity || 0), 0);

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header
        title={`Namaste, ${user?.full_name?.split(" ")[0] || "Farmer"}`}
        subtitle={user?.farmer_profile?.farm_village ? `📍 Village: ${user.farmer_profile.farm_village}` : "Verified Producer"}
        badge="FARMER"
      />

      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Quick Stats Grid */}
        <View style={styles.statsRow}>
          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>{listings.length}</Text>
            <Text style={styles.statLabel}>Active Listings</Text>
          </Card>

          <Card style={styles.statCard}>
            <Text style={styles.statNumber}>{totalQuantity.toFixed(1)} T</Text>
            <Text style={styles.statLabel}>Surplus Listed</Text>
          </Card>
        </View>

        {/* Responsible Farming Advisory */}
        <View style={styles.soilHealthBanner}>
          <Text style={styles.soilIcon}>🌱</Text>
          <View style={styles.soilTextContainer}>
            <Text style={styles.soilTitle}>Responsible Residue Advisory</Text>
            <Text style={styles.soilBody}>
              Remember to retain essential residue for mulch, soil nutrition, and livestock. Never sell critical field organic matter.
            </Text>
          </View>
        </View>

        {/* Action Button */}
        <Button
          title="+ Add Crop Residue Listing"
          onPress={() => {
            // Future week 3 screen
            alert("Week 3 Feature: Add Listing form connecting to POST /listings");
          }}
          variant="primary"
          style={styles.addBtn}
        />

        {/* My Listings Section */}
        <View style={styles.sectionHeaderRow}>
          <Text style={styles.sectionTitle}>My Agricultural Residue</Text>
          <Text style={styles.countText}>{listings.length} items</Text>
        </View>

        {listings.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyEmoji}>🌾</Text>
            <Text style={styles.emptyTitle}>No residue listings yet</Text>
            <Text style={styles.emptySubtitle}>
              List your surplus rice husk, wheat straw, cotton stalks or bagasse to connect with nearby biomass buyers.
            </Text>
          </Card>
        ) : (
          listings.map((item) => (
            <Card key={item.id} style={styles.listingCard}>
              <View style={styles.listingTop}>
                <Text style={styles.listingMaterial}>{item.material_name}</Text>
                <View style={styles.statusBadge}>
                  <Text style={styles.statusText}>{item.status.toUpperCase()}</Text>
                </View>
              </View>

              <Text style={styles.listingDetails}>
                Quantity: <Text style={styles.bold}>{item.available_quantity} {item.unit}</Text> • Price: <Text style={styles.bold}>₹{item.price_per_unit}/{item.unit}</Text>
              </Text>
              <Text style={styles.listingLocation}>📍 {item.location_name}</Text>
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
    color: Colors.primaryDark,
  },
  statLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 4,
    fontWeight: "500",
  },
  soilHealthBanner: {
    backgroundColor: Colors.successLight,
    borderColor: Colors.success,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 12,
  },
  soilIcon: {
    fontSize: 26,
    marginRight: 12,
  },
  soilTextContainer: {
    flex: 1,
  },
  soilTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.primaryDark,
  },
  soilBody: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 2,
    lineHeight: 16,
  },
  addBtn: {
    marginVertical: 8,
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
  statusBadge: {
    backgroundColor: Colors.primaryLight,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  statusText: {
    color: Colors.primaryDark,
    fontSize: 11,
    fontWeight: "700",
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
