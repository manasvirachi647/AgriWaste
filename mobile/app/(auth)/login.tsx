import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "../../constants/colors";
import { Input } from "../../components/Input";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { authService, UserRole } from "../../services/auth";

export default function LoginScreen() {
  const router = useRouter();

  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
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

  const handleLogin = async () => {
    setErrorMessage("");

    if (!usernameOrEmail.trim() || !password) {
      setErrorMessage("Please enter your username/email and password.");
      return;
    }

    setLoading(true);
    try {
      const result = await authService.login(usernameOrEmail.trim(), password);
      navigateToRoleDashboard(result.user.role);
    } catch (err: any) {
      const detail =
        err.response?.data?.detail ||
        err.message ||
        "Invalid username or password.";
      setErrorMessage(detail);
    } finally {
      setLoading(false);
    }
  };

  // Demo shortcut helper for fast testing
  const fillDemoAccount = (u: string, p: string) => {
    setUsernameOrEmail(u);
    setPassword(p);
  };

  return (
    <KeyboardAvoidingView
      style={styles.keyboardView}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Welcome Back</Text>
          <Text style={styles.subtitle}>
            Sign in to access your agricultural residue exchange account.
          </Text>
        </View>

        {errorMessage ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorBoxText}>{errorMessage}</Text>
          </View>
        ) : null}

        <Card>
          <Input
            label="Username or Email"
            placeholder="Enter your username or email"
            autoCapitalize="none"
            value={usernameOrEmail}
            onChangeText={setUsernameOrEmail}
          />

          <Input
            label="Password"
            placeholder="Enter your password"
            secureTextEntry
            value={password}
            onChangeText={setPassword}
          />

          <Button
            title="Sign In"
            onPress={handleLogin}
            loading={loading}
            variant="primary"
            style={styles.signInBtn}
          />
        </Card>

        {/* Demo Quick Fill for testing convenience */}
        <Card style={styles.demoCard}>
          <Text style={styles.demoTitle}>🧪 Quick Demo Logins</Text>
          <View style={styles.demoRow}>
            <TouchableOpacity
              style={styles.demoPill}
              onPress={() => fillDemoAccount("ramesh_farmer", "StrongPassword123!")}
            >
              <Text style={styles.demoPillText}>Farmer Demo</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.demoPill}
              onPress={() => fillDemoAccount("gujarat_biopower", "IndustryPass456!")}
            >
              <Text style={styles.demoPillText}>Buyer Demo</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.demoPill}
              onPress={() => fillDemoAccount("kisan_transport", "TruckFleet789!")}
            >
              <Text style={styles.demoPillText}>Transporter Demo</Text>
            </TouchableOpacity>
          </View>
        </Card>

        <View style={styles.footer}>
          <Button
            title="Don't have an account? Create one"
            onPress={() => router.push("/(auth)/select-role")}
            variant="outline"
          />
        </View>
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
    justifyContent: "center",
  },
  header: {
    marginBottom: 20,
  },
  title: {
    fontSize: 26,
    fontWeight: "800",
    color: Colors.textPrimary,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 6,
    lineHeight: 20,
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
  signInBtn: {
    marginTop: 12,
  },
  demoCard: {
    backgroundColor: "#F9FAFB",
    borderStyle: "dashed",
  },
  demoTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.textSecondary,
    marginBottom: 10,
  },
  demoRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  demoPill: {
    backgroundColor: Colors.primaryLight,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  demoPillText: {
    color: Colors.primaryDark,
    fontSize: 12,
    fontWeight: "600",
  },
  footer: {
    marginTop: 12,
  },
});
