import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { Colors } from "../../constants/colors";
import { Input } from "../../components/Input";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { authService, UserRole, RegisterPayload } from "../../services/auth";

export default function RegisterScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ role?: UserRole }>();
  const initialRole: UserRole = params.role || "farmer";

  const [role, setRole] = useState<UserRole>(initialRole);
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");

  // Role-specific fields
  const [farmVillage, setFarmVillage] = useState("");
  const [district, setDistrict] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [industryType, setIndustryType] = useState("");
  const [vehicleType, setVehicleType] = useState("");

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const navigateToRoleDashboard = (userRole: UserRole) => {
    switch (userRole) {
      case "farmer":
        router.replace("/(farmer)/dashboard");
        break;
      case "buyer":
        router.replace("/(buyer)/dashboard");
        break;
      case "aggregator":
        router.replace("/(aggregator)/dashboard");
        break;
      case "admin":
        router.replace("/(admin)/dashboard");
        break;
    }
  };

  const handleRegister = async () => {
    setErrorMessage("");

    if (!fullName.trim() || !username.trim() || !email.trim() || !password) {
      setErrorMessage("Please fill in all required fields.");
      return;
    }

    if (password.length < 6) {
      setErrorMessage("Password must be at least 6 characters long.");
      return;
    }

    setLoading(true);
    try {
      const payload: RegisterPayload = {
        username: username.trim(),
        email: email.trim().toLowerCase(),
        password,
        full_name: fullName.trim(),
        phone_number: phoneNumber.trim() || undefined,
        role,
        farm_village: farmVillage.trim() || undefined,
        district: district.trim() || undefined,
        company_name: companyName.trim() || undefined,
        industry_type: industryType.trim() || undefined,
        vehicle_type: vehicleType.trim() || undefined,
      };

      const result = await authService.register(payload);
      Alert.alert(
        "Account Created",
        `Welcome to AgriWaste Exchange, ${result.user.full_name}!`,
        [
          {
            text: "Proceed to Dashboard",
            onPress: () => navigateToRoleDashboard(result.user.role),
          },
        ]
      );
    } catch (err: any) {
      const detail =
        err.response?.data?.detail ||
        err.message ||
        "Registration failed. Please check your network and try again.";
      setErrorMessage(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.keyboardView}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Create Account</Text>
        <Text style={styles.roleBadgeText}>
          Registering as: <Text style={styles.roleHighlight}>{role.toUpperCase()}</Text>
        </Text>

        {errorMessage ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorBoxText}>{errorMessage}</Text>
          </View>
        ) : null}

        <Card>
          <Text style={styles.sectionHeader}>Personal & Account Info</Text>

          <Input
            label="Full Name *"
            placeholder="e.g. Ramesh Patel"
            value={fullName}
            onChangeText={setFullName}
          />

          <Input
            label="Username *"
            placeholder="e.g. ramesh_patel"
            autoCapitalize="none"
            value={username}
            onChangeText={setUsername}
          />

          <Input
            label="Email Address *"
            placeholder="e.g. ramesh@example.com"
            autoCapitalize="none"
            keyboardType="email-address"
            value={email}
            onChangeText={setEmail}
          />

          <Input
            label="Mobile Phone"
            placeholder="e.g. +91 98765 43210"
            keyboardType="phone-pad"
            value={phoneNumber}
            onChangeText={setPhoneNumber}
          />

          <Input
            label="Password *"
            placeholder="Minimum 6 characters"
            secureTextEntry
            value={password}
            onChangeText={setPassword}
          />
        </Card>

        {/* Role-specific details */}
        {role === "farmer" && (
          <Card>
            <Text style={styles.sectionHeader}>🌾 Farm Location</Text>
            <Input
              label="Village / Town"
              placeholder="e.g. Sanand"
              value={farmVillage}
              onChangeText={setFarmVillage}
            />
            <Input
              label="District / State"
              placeholder="e.g. Ahmedabad, Gujarat"
              value={district}
              onChangeText={setDistrict}
            />
          </Card>
        )}

        {role === "buyer" && (
          <Card>
            <Text style={styles.sectionHeader}>🏭 Industry Information</Text>
            <Input
              label="Company / Mill Name"
              placeholder="e.g. Green Power Biopellets Ltd"
              value={companyName}
              onChangeText={setCompanyName}
            />
            <Input
              label="Industry / Purpose"
              placeholder="e.g. Bio-coal, Paper, Composting"
              value={industryType}
              onChangeText={setIndustryType}
            />
          </Card>
        )}

        {role === "aggregator" && (
          <Card>
            <Text style={styles.sectionHeader}>🚛 Logistics Details</Text>
            <Input
              label="Vehicle Fleet / Type"
              placeholder="e.g. Tractor Trolley, 10-Tonne Truck"
              value={vehicleType}
              onChangeText={setVehicleType}
            />
            <Input
              label="Operating District"
              placeholder="e.g. Ahmedabad"
              value={district}
              onChangeText={setDistrict}
            />
          </Card>
        )}

        <Button
          title="Complete Registration"
          onPress={handleRegister}
          loading={loading}
          variant="primary"
          style={styles.submitButton}
        />

        <Button
          title="Already registered? Sign In"
          onPress={() => router.push("/(auth)/login")}
          variant="outline"
        />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  keyboardView: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  container: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "800",
    color: Colors.textPrimary,
  },
  roleBadgeText: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 4,
    marginBottom: 16,
  },
  roleHighlight: {
    color: Colors.primary,
    fontWeight: "700",
  },
  sectionHeader: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 12,
  },
  errorBox: {
    backgroundColor: Colors.errorLight,
    borderColor: Colors.error,
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 14,
  },
  errorBoxText: {
    color: Colors.error,
    fontSize: 13,
    fontWeight: "500",
  },
  submitButton: {
    marginTop: 10,
  },
});
