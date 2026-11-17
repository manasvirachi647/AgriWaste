import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "../../../constants/colors";
import { Header } from "../../../components/Header";
import { Input } from "../../../components/Input";
import { Button } from "../../../components/Button";
import { Card } from "../../../components/Card";
import { api } from "../../../services/api";

const COMMON_REQUIREMENTS = [
  "Rice Husk",
  "Wheat Straw",
  "Cotton Stalks",
  "Sugarcane Bagasse",
  "Groundnut Shells",
  "Mustard Stalks",
  "Corn Cob",
];

export default function AddRequirementScreen() {
  const router = useRouter();

  const [materialName, setMaterialName] = useState("Rice Husk");
  const [customMaterial, setCustomMaterial] = useState("");
  const [requiredQuantity, setRequiredQuantity] = useState("");
  const [unit, setUnit] = useState("tonnes");
  const [targetPriceMin, setTargetPriceMin] = useState("");
  const [targetPriceMax, setTargetPriceMax] = useState("");
  const [deliveryLocation, setDeliveryLocation] = useState("");
  const [qualitySpecifications, setQualitySpecifications] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const selectedMaterial = customMaterial.trim() ? customMaterial.trim() : materialName;

  const handleSubmit = async () => {
    setErrorMessage("");

    const parsedQty = parseFloat(requiredQuantity);
    const parsedMinPrice = targetPriceMin ? parseFloat(targetPriceMin) : undefined;
    const parsedMaxPrice = targetPriceMax ? parseFloat(targetPriceMax) : undefined;

    if (!selectedMaterial) {
      setErrorMessage("Please select or enter the required biomass material.");
      return;
    }

    if (isNaN(parsedQty) || parsedQty <= 0) {
      setErrorMessage("Please enter a required quantity greater than 0.");
      return;
    }

    if (!deliveryLocation.trim()) {
      setErrorMessage("Please enter your plant or delivery facility location.");
      return;
    }

    if (parsedMinPrice && parsedMaxPrice && parsedMinPrice > parsedMaxPrice) {
      setErrorMessage("Minimum target price cannot be higher than maximum target price.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        material_name: selectedMaterial,
        required_quantity: parsedQty,
        unit: unit,
        target_price_min: parsedMinPrice,
        target_price_max: parsedMaxPrice,
        delivery_location: deliveryLocation.trim(),
        quality_specifications: qualitySpecifications.trim() || undefined,
      };

      const res = await api.post("/requirements", payload);
      Alert.alert(
        "Requirement Published",
        `Your requirement for ${parsedQty} ${unit} of ${selectedMaterial} is now live. Farmers and aggregators can see your demand.`,
        [
          {
            text: "View Requirement",
            onPress: () => router.replace("/(buyer)/dashboard"),
          },
        ]
      );
    } catch (err: any) {
      const msg =
        err.response?.data?.detail ||
        err.message ||
        "Failed to publish requirement. Please try again.";
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <Header
        title="Publish Biomass Requirement"
        subtitle="Phase 4 • Buyer Module"
        onBack={() => router.back()}
        badge="BUYER"
      />

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {errorMessage ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>{errorMessage}</Text>
          </View>
        ) : null}

        {/* 1. Biomass Needed */}
        <Card>
          <Text style={styles.sectionTitle}>1. Required Raw Material</Text>
          <Text style={styles.hint}>Choose the biomass your facility requires</Text>

          <View style={styles.pillsContainer}>
            {COMMON_REQUIREMENTS.map((mat) => {
              const isSelected = materialName === mat && !customMaterial;
              return (
                <TouchableOpacity
                  key={mat}
                  onPress={() => {
                    setMaterialName(mat);
                    setCustomMaterial("");
                  }}
                  style={[styles.pill, isSelected && styles.pillSelected]}
                >
                  <Text style={[styles.pillText, isSelected && styles.pillTextSelected]}>
                    {mat}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>

          <Input
            label="Or enter custom material name"
            placeholder="e.g. Sawdust, Bagasse Pellets"
            value={customMaterial}
            onChangeText={(txt) => {
              setCustomMaterial(txt);
              if (txt) setMaterialName("");
            }}
          />
        </Card>

        {/* 2. Quantity & Target Price Range */}
        <Card>
          <Text style={styles.sectionTitle}>2. Demand Quantity & Target Price</Text>

          <View style={styles.row}>
            <View style={{ flex: 2, marginRight: 10 }}>
              <Input
                label="Required Quantity *"
                placeholder="e.g. 50"
                keyboardType="numeric"
                value={requiredQuantity}
                onChangeText={setRequiredQuantity}
                hint="Total biomass needed"
              />
            </View>

            <View style={{ flex: 1 }}>
              <Text style={styles.fieldLabel}>Unit</Text>
              <View style={styles.unitRow}>
                {["tonnes", "kg"].map((u) => (
                  <TouchableOpacity
                    key={u}
                    onPress={() => setUnit(u)}
                    style={[styles.unitBtn, unit === u && styles.unitBtnActive]}
                  >
                    <Text style={[styles.unitBtnText, unit === u && styles.unitBtnTextActive]}>
                      {u}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>

          <Text style={styles.fieldLabel}>Target Price Range (₹ per {unit})</Text>
          <View style={styles.row}>
            <View style={{ flex: 1, marginRight: 8 }}>
              <Input
                label="Min Price (₹)"
                placeholder="e.g. 2000"
                keyboardType="numeric"
                value={targetPriceMin}
                onChangeText={setTargetPriceMin}
              />
            </View>
            <View style={{ flex: 1 }}>
              <Input
                label="Max Price (₹)"
                placeholder="e.g. 2500"
                keyboardType="numeric"
                value={targetPriceMax}
                onChangeText={setTargetPriceMax}
              />
            </View>
          </View>
        </Card>

        {/* 3. Delivery & Quality Specs */}
        <Card>
          <Text style={styles.sectionTitle}>3. Delivery & Quality Standards</Text>

          <Input
            label="Delivery Facility / Plant Location *"
            placeholder="e.g. Plot 42, Sanand Industrial Estate, Ahmedabad"
            value={deliveryLocation}
            onChangeText={setDeliveryLocation}
            hint="Exact facility or unloading point for aggregators"
          />

          <Input
            label="Quality Specifications (Optional)"
            placeholder="e.g. Max 14% moisture content, free from plastic and stones, loose or baled"
            multiline
            numberOfLines={3}
            value={qualitySpecifications}
            onChangeText={setQualitySpecifications}
            style={{ height: 75 }}
          />
        </Card>

        <Button
          title="Publish Requirement & Find Suppliers"
          onPress={handleSubmit}
          loading={loading}
          variant="secondary"
          style={styles.submitBtn}
        />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  errorBox: {
    backgroundColor: Colors.errorLight,
    borderColor: Colors.error,
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 14,
  },
  errorText: {
    color: Colors.error,
    fontSize: 13,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  hint: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 10,
  },
  pillsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 12,
  },
  pill: {
    backgroundColor: "#F3F4F6",
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: Colors.cardBorder,
  },
  pillSelected: {
    backgroundColor: Colors.secondaryLight,
    borderColor: Colors.secondary,
  },
  pillText: {
    fontSize: 13,
    color: Colors.textPrimary,
  },
  pillTextSelected: {
    color: Colors.secondary,
    fontWeight: "700",
  },
  row: {
    flexDirection: "row",
    alignItems: "flex-start",
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textPrimary,
    marginBottom: 6,
  },
  unitRow: {
    flexDirection: "row",
    gap: 6,
    marginTop: 2,
  },
  unitBtn: {
    flex: 1,
    height: 48,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: Colors.white,
  },
  unitBtnActive: {
    backgroundColor: Colors.secondary,
    borderColor: Colors.secondary,
  },
  unitBtnText: {
    fontSize: 13,
    color: Colors.textPrimary,
    fontWeight: "600",
  },
  unitBtnTextActive: {
    color: Colors.white,
  },
  submitBtn: {
    marginTop: 12,
  },
});
