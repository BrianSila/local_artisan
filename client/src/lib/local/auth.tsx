import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { getStoredAuth, storeAuth, type User } from "./api";
const AuthContext = createContext<{
  user: User | null;
  ready: boolean;
  setSession: (token: string, user: User) => void;
  logout: () => Promise<void>;
}>({ user: null, ready: false, setSession: () => {}, logout: async () => {} });
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const query = useQueryClient();
  const router = useRouter();
  useEffect(() => {
    let hadSession = !!getStoredAuth();
    const sync = () => {
      const nextUser = getStoredAuth()?.user || null;
      setUser(nextUser);
      setReady(true);
      if (hadSession && !nextUser) {
        void query.cancelQueries().then(() => query.clear());
      }
      hadSession = !!nextUser;
      router.invalidate();
    };
    sync();
    window.addEventListener("local-auth", sync);
    return () => window.removeEventListener("local-auth", sync);
  }, [router, query]);
  const logout = async () => {
    await query.cancelQueries();
    query.clear();
    storeAuth(null);
    await router.navigate({ to: "/auth", replace: true });
  };
  return (
    <AuthContext.Provider
      value={{
        user,
        ready,
        setSession: (access_token, nextUser) => {
          storeAuth({ access_token, user: nextUser });
          setUser(nextUser);
        },
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
export const useAuth = () => useContext(AuthContext);
