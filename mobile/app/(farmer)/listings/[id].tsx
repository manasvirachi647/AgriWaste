import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  Alert,
  ActivityIndicator,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { Colors } from "../../../constants/colors";
import { Header } from "../../../components/Header";
import { Card } from "../../../components/Card";
import { Button } from "../../../components/Button";
import { api } from "../../../services/api";

interface ListingDetail {
  id: number;
  material_name: string;
  estimated_quantity: number;
  available_quantity: number;
  verified_quantity?: number;
  unit: string;
  price_per_unit: number;
  location_name: string;
  storage_type?: string;
  moisture_condition?: string;
  quality_notes?: string;
  status: string;
  created_at: string;
}

interface MatchingRequirement {
  id: number;
  material_name: string;
  required_quantity: number;
  unit: string;
  target_price_max?: number;
  delivery_location: string;
  status: string;
}

export default function ListingDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();

  const [listing, setListing] = useState<ListingDetail | null>(null);
  const [matchingDemands, setMatchingDemands] = useState<MatchingRequirement[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  const fetchDetails = async () => {
    try {
      const res = await api.get<ListingDetail>(`/listings/${id}`);
      setListing(res.data);

      // Fetch matching buyer requirements seeking this material
      const matchRes = await api.get<MatchingRequirement[]>(`/listings/${id}/matching-requirements`);
      setMatchingDemands(matchRes.data);
    } catch (err: any) {
      console.log("Error loading listing details:", err);
      Alert.alert("Error", "Could not load listing details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) fetchDetails();
  }, [id]);

  const handleDelete = () => {
    Alert.alert(
      "Cancel Listing",
      "Are you sure you want to cancel and remove this crop residue listing?",
      [
        { text: "No, Keep It", style: "cancel" },
        {
          text: "Yes, Cancel Listing",
          style: "destructive",
          onPress: async () => {
            setDeleting(true);
            try {
              await api.delete(`/listings/${id}`);
              Alert.alert("Listing Removed", "Your residue listing has been removed.", [
                { text: "OK", onPress: () => router.replace("/(farmer)/dashboard") },
              ]);
            } catch (err: any) {
              Alert.alert("Error", err.response?.data?.detail || "Could not delete listing.");
              setDeleting(false);
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={styles.loadingText}>Loading listing details...</Text>
      </SafeAreaView>
    );
  }

  if (!listing) {
    return (
      <SafeAreaView style={styles.center}>
        <Text style={styles.errorText}>Listing not found.</Text>
        <Button title="Back to Dashboard" onPress={() => router.back()} variant="outline" />
      </SafeAreaView>
    );
  }

  const potentialRevenue = listing.available_quantity * listing.price_per_unit;

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header
        title={listing.material_name}
        subtitle={`Listing #${listing.id} • Posted ${new Date(listing.created_at).toLocaleDateString()}`}
        onBack={() => router.back()}
        badge={listing.status.toUpperCase()}
      />

      <ScrollView contentContainerStyle={styles.container}>
        {/* Quantity & Value Card */}
        <Card style={styles.highlightCard}>
          <View style={styles.statRow}>
            <View>
              <Text style={styles.highlightLabel}>Available Quantity</Text>
              <Text style={styles.highlightValue}>
                {listing.available_quantity} <Text style={styles.unitText}>{listing.unit}</Text>
              </Text>
              <Text style={styles.subtext}>
                Initial Estimated: {listing.estimated_quantity} {listing.unit}
              </Text>
            </View>

            <View style={{ alignItems: "flex-end" }}>
              <Text style={styles.highlightLabel}>Expected Rate</Text>
              <Text style={styles.priceValue}>
                ₹{listing.price_per_unit}
                <Text style={styles.unitText}>/{listing.unit}</Text>
              </Text>
              <Text style={styles.revenueText}>
                Total Value: ₹{potentialRevenue.toLocaleString()}
              </Text>
            </View>
          </View>
        </Card>

        {/* Location & Storage Details */}
        <Card>
          <Text style={styles.sectionTitle}>Pickup & Quality Information</Text>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>📍 Location:</Text>
            <Text style={styles.detailValue}>{listing.location_name}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>📦 Storage Type:</Text>
            <Text style={styles.detailValue}>{listing.storage_type || "Standard storage"}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>💧 Moisture Level:</Text>
            <Text style={styles.detailValue}>{listing.moisture_condition || "Not specified"}</Text>
          </View>

          {listing.quality_notes ? (
            <View style={styles.notesBox}>
              <Text style={styles.notesLabel}>Farmer Quality Notes:</Text>
              <Text style={styles.notesText}>{listing.quality_notes}</Text>
            </View>
          ) : null}
        </Card>

        {/* Matching Industrial Demand */}
        <View style={styles.demandSectionHeader}>
          <Text style={styles.sectionTitle}>Matching Industrial Demand</Text>
          <Text style={styles.demandCount}>{matchingDemands.length} buyers</Text>
        </View>

        {matchingDemands.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyText}>
              No open buyer requirements found for {listing.material_name} right now. Your listing remains active in the public marketplace for new buyers to discover.
            </Text>
          </Card>
        ) : (
          matchingDemands.map((dm) => (
            <Card key={dm.id} style={styles.matchCard}>
              <View style={styles.matchTop}>
                <Text style={styles.matchTitle}>Requirement #{dm.id}: {dm.material_name}</Text>
                <View style={styles.matchBadge}>
                  <Text style={styles.matchBadgeText}>OPEN</Text>
                </View>
              </View>

              <Text style={styles.matchDetail}>
                Demanded: <Text style={styles.bold}>{dm.required_quantity} {dm.unit}</Text>
                {dm.target_price_max ? ` • Max Budget: ₹${dm.target_price_max}/${dm.unit}` : ""}
              </Text>
              <Text style={styles.matchLocation}>📍 Delivery to: {dm.delivery_location}</Text>
            </Card>
          ))
        )}

        {/* Actions */}
        <View style={styles.actionSection}>
          <Button
            title="Cancel / Delete Listing"
            onPress={handleDelete}
            loading={deleting}
            variant="danger"
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
    backgroundColor: Colors.primaryLight,
    borderColor: Colors.primary,
    borderWidth: 1.5,
  },
  statRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  highlightLabel: {
    fontSize: 12,
    color: Colors.primaryDark,
    fontWeight: "600",
  },
  highlightValue: {
    fontSize: 26,
    fontWeight: "800",
    color: Colors.primaryDark,
    marginTop: 2,
  },
  priceValue: {
    fontSize: 22,
    fontWeight: "800",
    color: Colors.primaryDark,
    marginTop: 2,
  },
  unitText: {
    fontSize: 14,
    fontWeight: "600",
  },
  subtext: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  revenueText: {
    fontSize: 12,
    color: Colors.primaryDark,
    fontWeight: "700",
    marginTop: 4,
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
  demandSectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 18,
    marginBottom: 6,
  },
  demandCount: {
    fontSize: 13,
    color: Colors.textSecondary,
  },
  emptyCard: {
    padding: 16,
  },
  emptyText: {
    fontSize: 13,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
  matchCard: {
    marginVertical: 6,
    borderLeftWidth: 4,
    borderLeftColor: Colors.secondary,
  },
  matchTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  matchTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  matchBadge: {
    backgroundColor: Colors.secondaryLight,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  matchBadgeText: {
    color: Colors.secondary,
    fontSize: 11,
    fontWeight: "700",
  },
  matchDetail: {
    fontSize: 13,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  matchLocation: {
    fontSize: 12,
    color: Colors.textMuted,
    marginTop: 2,
  },
  bold: {
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  actionSection: {
    marginTop: 20,
  },
});
