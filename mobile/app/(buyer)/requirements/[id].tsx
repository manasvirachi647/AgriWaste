import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  Alert,
  ActivityIndicator,
  TouchableOpacity,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { Colors } from "../../../constants/colors";
import { Header } from "../../../components/Header";
import { Card } from "../../../components/Card";
import { Button } from "../../../components/Button";
import { api } from "../../../services/api";

interface RequirementDetail {
  id: number;
  material_name: string;
  required_quantity: number;
  fulfilled_quantity: number;
  unit: string;
  target_price_min?: number;
  target_price_max?: number;
  delivery_location: string;
  quality_specifications?: string;
  status: string;
  created_at: string;
}

interface MatchingListing {
  id: number;
  material_name: string;
  available_quantity: number;
  unit: string;
  price_per_unit: number;
  location_name: string;
  storage_type?: string;
  moisture_condition?: string;
  farmer_id: number;
}

export default function RequirementDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();

  const [requirement, setRequirement] = useState<RequirementDetail | null>(null);
  const [matchingSuppliers, setMatchingSuppliers] = useState<MatchingListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);

  const fetchDetails = async () => {
    try {
      const res = await api.get<RequirementDetail>(`/requirements/${id}`);
      setRequirement(res.data);

      // Fetch matching farmer listings supplying this material
      const matchRes = await api.get<MatchingListing[]>(`/requirements/${id}/matching-listings`);
      setMatchingSuppliers(matchRes.data);
    } catch (err: any) {
      console.log("Error loading requirement details:", err);
      Alert.alert("Error", "Could not load requirement details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) fetchDetails();
  }, [id]);

  const handleCancelRequirement = () => {
    Alert.alert(
      "Close Requirement",
      "Are you sure you want to close this requirement? No further supplier matches will be aggregated.",
      [
        { text: "Keep Open", style: "cancel" },
        {
          text: "Yes, Close Requirement",
          style: "destructive",
          onPress: async () => {
            setCancelling(true);
            try {
              await api.patch(`/requirements/${id}`, { status: "cancelled" });
              Alert.alert("Requirement Closed", "This requirement is now closed.", [
                { text: "OK", onPress: () => router.replace("/(buyer)/dashboard") },
              ]);
            } catch (err: any) {
              Alert.alert("Error", err.response?.data?.detail || "Could not update requirement.");
              setCancelling(false);
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" color={Colors.secondary} />
        <Text style={styles.loadingText}>Loading requirement & matching suppliers...</Text>
      </SafeAreaView>
    );
  }

  if (!requirement) {
    return (
      <SafeAreaView style={styles.center}>
        <Text style={styles.errorText}>Requirement not found.</Text>
        <Button title="Back to Dashboard" onPress={() => router.back()} variant="outline" />
      </SafeAreaView>
    );
  }

  const remainingQty = Math.max(0, requirement.required_quantity - requirement.fulfilled_quantity);
  const progressPercent = Math.min(
    100,
    Math.round((requirement.fulfilled_quantity / requirement.required_quantity) * 100)
  );

  const totalMatchingSupply = matchingSuppliers.reduce(
    (acc, curr) => acc + (curr.available_quantity || 0),
    0
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header
        title={requirement.material_name}
        subtitle={`Requirement #${requirement.id} • Posted ${new Date(requirement.created_at).toLocaleDateString()}`}
        onBack={() => router.back()}
        badge={requirement.status.toUpperCase()}
      />

      <ScrollView contentContainerStyle={styles.container}>
        {/* Fulfillment Progress Card */}
        <Card style={styles.highlightCard}>
          <Text style={styles.highlightLabel}>Biomass Demand Fulfillment</Text>

          <View style={styles.progressRow}>
            <View>
              <Text style={styles.qtyTotal}>
                {requirement.required_quantity} <Text style={styles.unitText}>{requirement.unit}</Text>
              </Text>
              <Text style={styles.subtext}>Total Biomass Required</Text>
            </View>

            <View style={{ alignItems: "flex-end" }}>
              <Text style={styles.qtyRemaining}>
                {remainingQty} <Text style={styles.unitText}>{requirement.unit}</Text>
              </Text>
              <Text style={styles.subtext}>Remaining to Procure</Text>
            </View>
          </View>

          {/* Progress Bar */}
          <View style={styles.progressBarTrack}>
            <View style={[styles.progressBarFill, { width: `${progressPercent}%` }]} />
          </View>
          <Text style={styles.progressLabel}>
            {requirement.fulfilled_quantity} {requirement.unit} fulfilled ({progressPercent}%)
          </Text>
        </Card>

        {/* Demand Specifications */}
        <Card>
          <Text style={styles.sectionTitle}>Procurement & Plant Details</Text>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>📍 Delivery Plant:</Text>
            <Text style={styles.detailValue}>{requirement.delivery_location}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>💰 Target Price:</Text>
            <Text style={styles.detailValue}>
              {requirement.target_price_min || requirement.target_price_max
                ? `₹${requirement.target_price_min || 0} - ₹${requirement.target_price_max || "Open"}/${requirement.unit}`
                : "Open / Market Rate"}
            </Text>
          </View>

          {requirement.quality_specifications ? (
            <View style={styles.notesBox}>
              <Text style={styles.notesLabel}>Quality Specifications:</Text>
              <Text style={styles.notesText}>{requirement.quality_specifications}</Text>
            </View>
          ) : null}
        </Card>

        {/* Live Matching Farmer Supply */}
        <View style={styles.supplierSectionHeader}>
          <Text style={styles.sectionTitle}>Available Farmer Suppliers</Text>
          <Text style={styles.supplierCount}>
            {matchingSuppliers.length} suppliers ({totalMatchingSupply.toFixed(1)} {requirement.unit} available)
          </Text>
        </View>

        {matchingSuppliers.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyEmoji}>🌾</Text>
            <Text style={styles.emptyTitle}>No matching listings available</Text>
            <Text style={styles.emptyText}>
              There are currently no active farmer listings for {requirement.material_name}. As soon as farmers list their harvest residue, they will automatically appear here.
            </Text>
          </Card>
        ) : (
          matchingSuppliers.map((supplier) => (
            <Card key={supplier.id} style={styles.supplierCard}>
              <View style={styles.supplierTop}>
                <View>
                  <Text style={styles.supplierMaterial}>Listing #{supplier.id}: {supplier.material_name}</Text>
                  <Text style={styles.supplierLocation}>📍 {supplier.location_name}</Text>
                </View>
                <View style={styles.priceBadge}>
                  <Text style={styles.priceBadgeText}>₹{supplier.price_per_unit}/{supplier.unit}</Text>
                </View>
              </View>

              <View style={styles.supplierSpecsRow}>
                <Text style={styles.supplierQty}>
                  Available: <Text style={styles.bold}>{supplier.available_quantity} {supplier.unit}</Text>
                </Text>
                {supplier.storage_type ? (
                  <Text style={styles.supplierStorage}>📦 {supplier.storage_type}</Text>
                ) : null}
              </View>

              {supplier.moisture_condition ? (
                <Text style={styles.moistureText}>💧 Moisture: {supplier.moisture_condition}</Text>
              ) : null}
            </Card>
          ))
        )}

        {/* Actions */}
        {requirement.status === "open" ? (
          <View style={styles.actionSection}>
            <Button
              title="Close Requirement"
              onPress={handleCancelRequirement}
              loading={cancelling}
              variant="outline"
            />
          </View>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    color: Colors.textSecondary,
    fontSize: 14,
  },
  errorText: {
    color: Colors.error,
    fontSize: 16,
    marginBottom: 16,
  },
  container: {
    padding: 16,
    paddingBottom: 40,
  },
  highlightCard: {
    backgroundColor: Colors.secondaryLight,
    borderColor: Colors.secondary,
    borderWidth: 1.5,
  },
  highlightLabel: {
    fontSize: 12,
    color: Colors.secondary,
    fontWeight: "700",
    textTransform: "uppercase",
  },
  progressRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 8,
    marginBottom: 12,
  },
  qtyTotal: {
    fontSize: 24,
    fontWeight: "800",
    color: Colors.textPrimary,
  },
  qtyRemaining: {
    fontSize: 24,
    fontWeight: "800",
    color: Colors.secondary,
  },
  unitText: {
    fontSize: 14,
    fontWeight: "600",
  },
  subtext: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  progressBarTrack: {
    height: 10,
    backgroundColor: "#E5E7EB",
    borderRadius: 5,
    overflow: "hidden",
  },
  progressBarFill: {
    height: "100%",
    backgroundColor: Colors.secondary,
    borderRadius: 5,
  },
  progressLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 6,
    textAlign: "right",
    fontWeight: "500",
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 8,
  },
  detailRow: {
    flexDirection: "row",
    marginVertical: 4,
  },
  detailLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textSecondary,
    width: 130,
  },
  detailValue: {
    fontSize: 13,
    color: Colors.textPrimary,
    flex: 1,
    fontWeight: "500",
  },
  notesBox: {
    backgroundColor: "#F9FAFB",
    padding: 10,
    borderRadius: 8,
    marginTop: 10,
  },
  notesLabel: {
    fontSize: 12,
    fontWeight: "700",
    color: Colors.textSecondary,
  },
  notesText: {
    fontSize: 13,
    color: Colors.textPrimary,
    marginTop: 2,
    lineHeight: 18,
  },
  supplierSectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 18,
    marginBottom: 6,
  },
  supplierCount: {
    fontSize: 12,
    color: Colors.textSecondary,
    fontWeight: "500",
  },
  emptyCard: {
    alignItems: "center",
    paddingVertical: 24,
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
  emptyText: {
    fontSize: 13,
    color: Colors.textSecondary,
    textAlign: "center",
    paddingHorizontal: 16,
    marginTop: 4,
    lineHeight: 18,
  },
  supplierCard: {
    marginVertical: 6,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  supplierTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  supplierMaterial: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  supplierLocation: {
    fontSize: 12,
    color: Colors.textMuted,
    marginTop: 2,
  },
  priceBadge: {
    backgroundColor: Colors.primaryLight,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  priceBadgeText: {
    color: Colors.primaryDark,
    fontSize: 12,
    fontWeight: "800",
  },
  supplierSpecsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 8,
  },
  supplierQty: {
    fontSize: 13,
    color: Colors.textSecondary,
  },
  supplierStorage: {
    fontSize: 12,
    color: Colors.accent,
  },
  moistureText: {
    fontSize: 12,
    color: Colors.textMuted,
    marginTop: 4,
  },
  bold: {
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  actionSection: {
    marginTop: 20,
  },
});
