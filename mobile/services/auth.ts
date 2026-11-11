import { api, setAuthToken } from "./api";

export type UserRole = "farmer" | "buyer" | "aggregator" | "admin";

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name: string;
  phone_number?: string;
  role: UserRole;
  is_active: boolean;
  farmer_profile?: {
    farm_village?: string;
    district?: string;
    land_size_acres?: number;
  };
  buyer_profile?: {
    company_name?: string;
    industry_type?: string;
  };
  aggregator_profile?: {
    vehicle_type?: string;
    capacity_tonnes?: number;
  };
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  full_name: string;
  phone_number?: string;
  role: UserRole;
  farm_village?: string;
  district?: string;
  company_name?: string;
  industry_type?: string;
  vehicle_type?: string;
}

// In-memory token cache for cross-platform compatibility
let cachedUser: UserProfile | null = null;

export const authService = {
  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/register", payload);
    const { access_token, user } = response.data;
    setAuthToken(access_token);
    cachedUser = user;
    return response.data;
  },

  async login(username_or_email: string, password: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/login", {
      username_or_email,
      password,
    });
    const { access_token, user } = response.data;
    setAuthToken(access_token);
    cachedUser = user;
    return response.data;
  },

  async getCurrentUser(): Promise<UserProfile> {
    const response = await api.get<UserProfile>("/auth/me");
    cachedUser = response.data;
    return response.data;
  },

  logout(): void {
    setAuthToken(null);
    cachedUser = null;
  },

  getCachedUser(): UserProfile | null {
    return cachedUser;
  },
};
