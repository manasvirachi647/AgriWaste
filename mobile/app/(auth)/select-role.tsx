import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "../../constants/colors";
import { Button } from "../../components/Button";
import { UserRole } from "../../services/auth";

interface RoleOption {
  role: UserRole;
  title: string;
  emoji: string;
  subtitle: string;
}

const ROLES: RoleOption[] = [
  {
    role: "farmer",
    title: "Farmer / Producer",
    emoji: "👨‍🌾",
    subtitle: "List crop residue (rice husk, straw, bagasse), view matching industrial demand, and earn fair prices.",
  },
  {
    role: "buyer",
    title: "Industrial Buyer",
    emoji: "🏭",
    subtitle: "Publish bulk biomass requirements, source from aggregated farmers, and manage delivery orders.",
  },
  {
    role: "aggregator",
    title: "Transporter / Aggregator",
    emoji: "🚛",
    subtitle: "Accept transport jobs, coordinate collection from multiple rural farms, and update delivery status.",
  },
  {
    role: "admin",
    title: "Administrator",
    emoji: "🛡️",
    subtitle: "Oversee marketplace activity, review disputed orders, and maintain platform integrity.",
  },
];

export default function SelectRoleScreen() {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState<UserRole>("farmer");

  const handleContinue = () => {
    router.push({
      pathname: "/(auth)/register",
      params: { role: selectedRole },
    });
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.heading}>Choose Your Role</Text>
      <Text style={styles.subheading}>
        Select how you want to participate in the AgriWaste Exchange network.
      </Text>

      <View style={styles.rolesList}>
        {ROLES.map((item) => {
          const isSelected = selectedRole === item.role;
          return (
            <TouchableOpacity
              key={item.role}
              activeOpacity={0.8}
              onPress={() => setSelectedRole(item.role)}
              style={[
                styles.roleCard,
                isSelected && styles.roleCardSelected,
              ]}
            >
              <View style={styles.roleHeader}>
                <Text style={styles.roleEmoji}>{item.emoji}</Text>
                <View style={styles.roleTitleContainer}>
                  <Text style={[styles.roleTitle, isSelected && styles.roleTitleSelected]}>
                    {item.title}
                  </Text>
                </View>
                <View style={[styles.radioCircle, isSelected && styles.radioCircleSelected]}>
                  {isSelected && <View style={styles.radioInner} />}
                </View>
              </View>
              <Text style={styles.roleSubtitle}>{item.subtitle}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      <Button
        title={`Continue as ${ROLES.find((r) => r.role === selectedRole)?.title}`}
        onPress={handleContinue}
        variant="primary"
        style={styles.continueButton}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: Colors.background,
  },
  heading: {
    fontSize: 24,
    fontWeight: "800",
    color: Colors.textPrimary,
  },
  subheading: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 6,
    marginBottom: 20,
    lineHeight: 20,
  },
  rolesList: {
    marginBottom: 20,
  },
  roleCard: {
    backgroundColor: Colors.white,
    borderRadius: 12,
    padding: 16,
    marginVertical: 8,
    borderWidth: 1.5,
    borderColor: Colors.cardBorder,
  },
  roleCardSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.primaryLight,
  },
  roleHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  roleEmoji: {
    fontSize: 28,
    marginRight: 12,
  },
  roleTitleContainer: {
    flex: 1,
  },
  roleTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  roleTitleSelected: {
    color: Colors.primaryDark,
  },
  radioCircle: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: Colors.border,
    justifyContent: "center",
    alignItems: "center",
  },
  radioCircleSelected: {
    borderColor: Colors.primary,
  },
  radioInner: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: Colors.primary,
  },
  roleSubtitle: {
    fontSize: 13,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
  continueButton: {
    marginTop: 10,
  },
});
