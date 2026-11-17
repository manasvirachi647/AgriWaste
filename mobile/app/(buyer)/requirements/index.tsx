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

interface RequirementItem {
  id: number;
  material_name: string;
  required_quantity: number;
  fulfilled_quantity: number;
  unit: string;
  target_price_max?: number;
  delivery_location: string;
  status: string;
  created_at: string;
}

export default function BuyerRequirementsListScreen() {
  const router = useRouter();
  const [requirements, setRequirements] = useState<RequirementItem[]>([]);
  const [filterText, setFilterText] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [refreshing, setRefreshing] = useState(false);

  const fetchRequirements = async () => {
    try {
      const res = await api.get<RequirementItem[]>("/requirements/my");
      setRequirements(res.data);
    } catch (err) {
      console.log("Error loading requirements:", err);
    }
  };

  useEffect(() => {
    fetchRequirements();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchRequirements();
    setRefreshing(false);
  };

  const filteredRequirements = requirements.filter((item) => {
    const matchesSearch = item.material_name.toLowerCase().includes(filterText.toLowerCase()) ||
      item.delivery_location.toLowerCase().includes(filterText.toLowerCase());
    const matchesStatus = selectedStatus === "ALL" || item.status.toUpperCase() === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header
        title="My Biomass Requirements"
        subtitle="Manage procurement demands and supplier matches"
        onBack={() => router.back()}
        badge="BUYER"
      />

      <View style={styles.searchBarContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search by required biomass or plant location..."
          placeholderTextColor={Colors.textMuted}
          value={filterText}
          onChangeText={setFilterText}
        />
      </View>

      {/* Filter Tabs */}
      <View style={styles.tabRow}>
        {["ALL", "OPEN", "PARTIALLY_FULFILLED", "FULFILLED", "CANCELLED"].map((st) => (
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
          title="+ Publish New Biomass Requirement"
          onPress={() => router.push("/(buyer)/requirements/add")}
          variant="secondary"
          style={styles.addBtn}
        />

        {filteredRequirements.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyEmoji}>📋</Text>
            <Text style={styles.emptyTitle}>No requirements found</Text>
            <Text style={styles.emptySubtitle}>
              {filterText ? "No demands match your search criteria." : "You have not published any requirements under this status."}
            </Text>
          </Card>
        ) : (
          filteredRequirements.map((item) => (
            <TouchableOpacity
              key={item.id}
              activeOpacity={0.8}
              onPress={() => router.push(`/(buyer)/requirements/${item.id}`)}
            >
              <Card style={styles.reqCard}>
                <View style={styles.reqTop}>
                  <Text style={styles.reqMaterial}>{item.material_name}</Text>
                  <View style={styles.statusBadge}>
                    <Text style={styles.statusText}>{item.status.toUpperCase()}</Text>
                  </View>
                </View>

                <Text style={styles.reqDetails}>
                  Needed: <Text style={styles.bold}>{item.required_quantity} {item.unit}</Text>
                  {item.target_price_max ? ` • Max: ₹${item.target_price_max}/${item.unit}` : ""}
                </Text>
                <Text style={styles.reqLocation}>📍 {item.delivery_location}</Text>
                <Text style={styles.dateText}>Published: {new Date(item.created_at).toLocaleDateString()}</Text>
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
    gap: 6,
    flexWrap: "wrap",
  },
  tabBtn: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 14,
    backgroundColor: "#F3F4F6",
  },
  tabBtnActive: {
    backgroundColor: Colors.secondary,
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
    paddingVertical: 2,
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
  bold: {
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  reqLocation: {
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
