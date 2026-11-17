import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  TouchableOpacity,
  RefreshControl,
  TextInput,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "../../../constants/colors";
import { Header } from "../../../components/Header";
import { Card } from "../../../components/Card";
import { Button } from "../../../components/Button";
import { api } from "../../../services/api";

interface ListingItem {
  id: number;
  material_name: string;
  available_quantity: number;
  estimated_quantity: number;
  unit: string;
  price_per_unit: number;
  location_name: string;
  status: string;
  created_at: string;
}

export default function FarmerListingsListScreen() {
  const router = useRouter();
  const [listings, setListings] = useState<ListingItem[]>([]);
  const [filterText, setFilterText] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [refreshing, setRefreshing] = useState(false);

  const fetchListings = async () => {
    try {
      const res = await api.get<ListingItem[]>("/listings/my");
      setListings(res.data);
    } catch (err) {
      console.log("Error loading listings:", err);
    }
  };

  useEffect(() => {
    fetchListings();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchListings();
    setRefreshing(false);
  };

  const filteredListings = listings.filter((item) => {
    const matchesSearch = item.material_name.toLowerCase().includes(filterText.toLowerCase()) ||
      item.location_name.toLowerCase().includes(filterText.toLowerCase());
    const matchesStatus = selectedStatus === "ALL" || item.status.toUpperCase() === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header
        title="My Crop Residue Listings"
        subtitle="Manage active and past biomass listings"
        onBack={() => router.back()}
        badge="FARMER"
      />

      <View style={styles.searchBarContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search by crop material or village..."
          placeholderTextColor={Colors.textMuted}
          value={filterText}
          onChangeText={setFilterText}
        />
      </View>

      {/* Filter Tabs */}
      <View style={styles.tabRow}>
        {["ALL", "AVAILABLE", "RESERVED", "COMPLETED"].map((st) => (
          <TouchableOpacity
            key={st}
            onPress={() => setSelectedStatus(st)}
            style={[styles.tabBtn, selectedStatus === st && styles.tabBtnActive]}
          >
            <Text style={[styles.tabText, selectedStatus === st && styles.tabTextActive]}>
              {st}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <Button
          title="+ Add New Residue Listing"
          onPress={() => router.push("/(farmer)/listings/add")}
          variant="primary"
          style={styles.addBtn}
        />

        {filteredListings.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyEmoji}>🌾</Text>
            <Text style={styles.emptyTitle}>No matching listings found</Text>
            <Text style={styles.emptySubtitle}>
              {filterText ? "Try adjusting your search query." : "You have not listed any crop residue under this category yet."}
            </Text>
          </Card>
        ) : (
          filteredListings.map((item) => (
            <TouchableOpacity
              key={item.id}
              activeOpacity={0.8}
              onPress={() => router.push(`/(farmer)/listings/${item.id}`)}
            >
              <Card style={styles.listingCard}>
                <View style={styles.listingTop}>
                  <Text style={styles.listingMaterial}>{item.material_name}</Text>
                  <View style={[
                    styles.statusBadge,
                    item.status === "available" ? styles.statusAvailable : styles.statusOther
                  ]}>
                    <Text style={styles.statusText}>{item.status.toUpperCase()}</Text>
                  </View>
                </View>

                <Text style={styles.listingDetails}>
                  Stock: <Text style={styles.bold}>{item.available_quantity} {item.unit}</Text> • Rate: <Text style={styles.bold}>₹{item.price_per_unit}/{item.unit}</Text>
                </Text>
                <Text style={styles.listingLocation}>📍 {item.location_name}</Text>
                <Text style={styles.dateText}>Posted on: {new Date(item.created_at).toLocaleDateString()}</Text>
              </Card>
            </TouchableOpacity>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  searchBarContainer: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 6,
    backgroundColor: Colors.white,
  },
  searchInput: {
    height: 44,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 8,
    paddingHorizontal: 12,
    backgroundColor: Colors.background,
    color: Colors.textPrimary,
    fontSize: 14,
  },
  tabRow: {
    flexDirection: "row",
    backgroundColor: Colors.white,
    paddingHorizontal: 16,
    paddingBottom: 10,
    gap: 8,
  },
  tabBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: "#F3F4F6",
  },
  tabBtnActive: {
    backgroundColor: Colors.primary,
  },
  tabText: {
    fontSize: 11,
    fontWeight: "600",
    color: Colors.textSecondary,
  },
  tabTextActive: {
    color: Colors.white,
  },
  container: {
    padding: 16,
    paddingBottom: 30,
  },
  addBtn: {
    marginBottom: 12,
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
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  statusAvailable: {
    backgroundColor: Colors.primaryLight,
  },
  statusOther: {
    backgroundColor: "#F3F4F6",
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
  dateText: {
    fontSize: 11,
    color: Colors.textMuted,
    marginTop: 4,
  },
  emptyCard: {
    alignItems: "center",
    paddingVertical: 30,
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
  },
});
