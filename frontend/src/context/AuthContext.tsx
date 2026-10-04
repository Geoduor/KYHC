import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  api,
  clearToken,
  getToken,
  loginRequest,
  setToken,
} from "../lib/api";
import type { Role, User } from "../types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  canManage: boolean;
  canCoach: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const ADMIN_ROLES: Role[] = ["SUPER_ADMIN", "CLUB_ADMIN"];

const MANAGEMENT_ROLES: Role[] = [
  ...ADMIN_ROLES,
  "TEAM_MANAGER",
];

const COACHING_ROLES: Role[] = [
  ...ADMIN_ROLES,
  "COACH",
  "ASSISTANT_COACH",
];

export function hasRole(
  user: User | null,
  allowed: Role[],
): boolean {
  return user !== null && allowed.includes(user.role);
}

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();

    if (!token) {
      setLoading(false);
      return;
    }

    api
      .get<User>("/users/me")
      .then(setUser)
      .catch(() => {
        clearToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const token = await loginRequest(email, password);

      setToken(token);

      try {
        const profile = await api.get<User>("/users/me");

        setUser(profile);
      } catch (error) {
        clearToken();
        throw error;
      }
    },
    [],
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      login,
      logout,
      isAdmin: hasRole(user, ADMIN_ROLES),
      canManage: hasRole(user, MANAGEMENT_ROLES),
      canCoach: hasRole(user, COACHING_ROLES),
    }),
    [user, loading, login, logout],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
}
