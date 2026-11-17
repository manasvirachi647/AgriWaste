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

const COMMON_MATERIALS = [
  "Rice Husk",
  "Wheat Straw",
  "Cotton Stalks",
  "Sugarcane Bagasse",
  "Groundnut Shells",
  "Mustard Stalks",
  "Corn Cob",
  "Soybean Straw",
];

const STORAGE_OPTIONS = [
  "Dry covered shed",
  "Open field / Heap",
  "Silo storage",
  "Baled & Stacked",
];

const MOISTURE_OPTIONS = [
  "Dry (< 12%)",
  "Medium / Semi-dry (12-20%)",
  "High / Freshly Harvested (> 20%)",
];

export default function AddListingScreen() {
  const router = useRouter();

  const [materialName, setMaterialName] = useState("Rice Husk");
  const [customMaterial, setCustomMaterial] = useState("");
  const [quantity, setQuantity] = useState("");
  const [unit, setUnit] = useState("tonnes");
  const [pricePerUnit, setPricePerUnit] = useState("");
  const [locationName, setLocationName] = useState("");
  const [storageType, setStorageType] = useState(STORAGE_OPTIONS[0]);
  const [moistureCondition, setMoistureCondition] = useState(MOISTURE_OPTIONS[0]);
  const [qualityNotes, setQualityNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const selectedMaterial = customMaterial.trim() ? customMaterial.trim() : materialName;

  const handleSubmit = async () => {
    setErrorMessage("");

    const parsedQty = parseFloat(quantity);
    const parsedPrice = parseFloat(pricePerUnit);

    if (!selectedMaterial) {
      setErrorMessage("Please select or enter the crop residue material.");
      return;
    }

    if (isNaN(parsedQty) || parsedQty <= 0) {
      setErrorMessage("Please enter a valid surplus quantity greater than 0.");
      return;
    }

    if (isNaN(parsedPrice) || parsedPrice <= 0) {
      setErrorMessage("Please enter an expected price per unit.");
      return;
    }

    if (!locationName.trim()) {
      setErrorMessage("Please enter your farm or pickup location (Village / District).");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        material_name: selectedMaterial,
        estimated_quantity: parsedQty,
        unit: unit,
        price_per_unit: parsedPrice,
        location_name: locationName.trim(),
        storage_type: storageType,
        moisture_condition: moistureCondition,
        quality_notes: qualityNotes.trim() || undefined,
      };

      const res = await api.post("/listings", payload);
      Alert.alert(
        "Residue Listed Successfully",
        `Your listing for ${parsedQty} ${unit} of ${selectedMaterial} is now active and discoverable by industrial buyers.`,
        [
          {
            text: "View My Listings",
            onPress: () => router.replace("/(farmer)/dashboard"),
          },
        ]
      );
    } catch (err: any) {
      const msg =
        err.response?.data?.detail ||
        err.message ||
        "Failed to create listing. Please try again.";
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
        title="Add Crop Residue Listing"
        subtitle="Phase 3 • Farmer Module"
        onBack={() => router.back()}
        badge="FARMER"
      />

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Soil Health Banner */}
        <View style={styles.advisoryBanner}>
          <Text style={styles.advisoryTitle}>🌱 Sustainable Residue Reminder</Text>
          <Text style={styles.advisoryText}>
            Sell only what is genuinely surplus! Always retain the necessary stubble for soil conservation, livestock fodder, and local organic compost.
          </Text>
        </View>

        {errorMessage ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>{errorMessage}</Text>
          </View>
        ) : null}

        {/* 1. Crop Material Selection */}
        <Card>
          <Text style={styles.sectionTitle}>1. Crop Residue Type</Text>
          <Text style={styles.hint}>Choose common biomass or enter custom name</Text>

          <View style={styles.pillsContainer}>
            {COMMON_MATERIALS.map((mat) => {
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
            label="Or enter custom crop material"
            placeholder="e.g. Rice Straw, Groundnut Vines"
            value={customMaterial}
            onChangeText={(txt) => {
              setCustomMaterial(txt);
              if (txt) setMaterialName("");
            }}
          />
        </Card>

        {/* 2. Quantity & Pricing */}
        <Card>
          <Text style={styles.sectionTitle}>2. Quantity & Expected Price</Text>

          <View style={styles.row}>
            <View style={{ flex: 2, marginRight: 10 }}>
              <Input
                label="Surplus Quantity *"
                placeholder="e.g. 5.0"
                keyboardType="numeric"
                value={quantity}
                onChangeText={setQuantity}
                hint="Estimated surplus amount"
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

          <Input
            label={`Expected Price (₹ per ${unit}) *`}
            placeholder="e.g. 2400"
            keyboardType="numeric"
            value={pricePerUnit}
            onChangeText={setPricePerUnit}
            hint={`Price for 1 ${unit} of ${selectedMaterial}`}
          />
        </Card>

        {/* 3. Farm Location & Storage */}
        <Card>
          <Text style={styles.sectionTitle}>3. Pickup Location & Storage Quality</Text>

          <Input
            label="Farm / Pickup Location *"
            placeholder="e.g. Sanand Village, Ahmedabad, Gujarat"
            value={locationName}
            onChangeText={setLocationName}
            hint="Village, Taluka, and District for aggregator pickup"
          />

          <Text style={styles.fieldLabel}>Storage Condition</Text>
          <View style={styles.optionsGrid}>
            {STORAGE_OPTIONS.map((opt) => (
              <TouchableOpacity
                key={opt}
                onPress={() => setStorageType(opt)}
                style={[styles.optionItem, storageType === opt && styles.optionItemActive]}
              >
                <Text style={[styles.optionText, storageType === opt && styles.optionTextActive]}>
                  {opt}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={[styles.fieldLabel, { marginTop: 12 }]}>Moisture Level</Text>
          <View style={styles.optionsGrid}>
            {MOISTURE_OPTIONS.map((opt) => (
              <TouchableOpacity
                key={opt}
                onPress={() => setMoistureCondition(opt)}
                style={[styles.optionItem, moistureCondition === opt && styles.optionItemActive]}
              >
                <Text style={[styles.optionText, moistureCondition === opt && styles.optionTextActive]}>
                  {opt}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Input
            label="Quality Notes (Optional)"
            placeholder="e.g. Clean dry harvest, free of soil and stones, bagged in 50kg bags"
            multiline
            numberOfLines={3}
            value={qualityNotes}
            onChangeText={setQualityNotes}
            style={{ height: 70 }}
          />
        </Card>

        <Button
          title="Publish Residue Listing"
          onPress={handleSubmit}
          loading={loading}
          variant="primary"
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
  advisoryBanner: {
    backgroundColor: Colors.successLight,
    borderColor: Colors.success,
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 14,
  },
  advisoryTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.primaryDark,
    marginBottom: 4,
  },
  advisoryText: {
    fontSize: 12,
    color: Colors.textSecondary,
    lineHeight: 16,
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
    backgroundColor: Colors.primaryLight,
    borderColor: Colors.primary,
  },
  pillText: {
    fontSize: 13,
    color: Colors.textPrimary,
  },
  pillTextSelected: {
    color: Colors.primaryDark,
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
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  unitBtnText: {
    fontSize: 13,
    color: Colors.textPrimary,
    fontWeight: "600",
  },
  unitBtnTextActive: {
    color: Colors.white,
  },
  optionsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 8,
  },
  optionItem: {
    backgroundColor: "#F9FAFB",
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  optionItemActive: {
    backgroundColor: Colors.primaryLight,
    borderColor: Colors.primary,
  },
  optionText: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  optionTextActive: {
    color: Colors.primaryDark,
    fontWeight: "700",
  },
  submitBtn: {
    marginTop: 12,
  },
});
