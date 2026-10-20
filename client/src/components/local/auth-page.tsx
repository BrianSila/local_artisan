import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ApiError, api, type User } from "@/lib/local/api";
import { useAuth } from "@/lib/local/auth";
export interface AuthSearch {
  mode?: "login" | "register" | undefined;
  role?: "customer" | "artisan" | undefined;
  redirect?: string | undefined;
}
export function AuthPage({ search }: { search: AuthSearch }) {
  const [mode, setMode] = useState(search.mode || "login");
  const [role, setRole] = useState<"customer" | "artisan">(search.role || "customer");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);
  const { user, setSession } = useAuth();
  const navigate = useNavigate();
  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setBusy(true);
    const fields = new FormData(e.currentTarget);
    const body = {
      email: String(fields.get("email")).trim(),
      password: String(fields.get("password")),
    };
    try {
      if (mode === "register") {
        const result = await api<{ message: string; user: User }>("/auth/register", {
          method: "POST",
          body: {
            ...body,
            name: String(fields.get("name")).trim(),
            phone: String(fields.get("phone") || "").trim() || undefined,
            role,
          },
        });
        setSuccess(result.message || "Account created. Log in to continue.");
        setMode("login");
      } else {
        const result = await api<{ message: string; access_token: string; user: User }>(
          "/auth/login",
          { method: "POST", body },
        );
        setSession(result.access_token, result.user);
        let destination = search.redirect;
        if (!destination && result.user.role === "artisan") {
          try {
            await api("/artisan/profile");
            destination = "/workspace";
          } catch (profileError) {
            if (profileError instanceof ApiError && profileError.status === 404) {
              destination = "/onboarding";
            } else {
              throw profileError;
            }
          }
        }
        await navigate({ to: destination || "/workspace" });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Please try again.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="container page-main auth-page-main">
      <div className="auth-layout">
        <div className="section-label">WELCOME TO LOCAL ARTISAN</div>
        <h1 className="page-title">
          {user
            ? `Welcome, ${user.name}`
            : mode === "login"
              ? "Good to see you again."
              : "Your next connection starts here."}
        </h1>
        {user ? (
          <>
            <p className="page-subtitle">You’re signed in and ready to go.</p>
            <Button onClick={() => navigate({ to: "/workspace" })}>
              Go to my account <ArrowRight />
            </Button>
          </>
        ) : (
          <>
            <div className="segmented auth-tabs" role="tablist" aria-label="Authentication mode">
              <Button
                variant="ghost"
                className={mode === "login" ? "selected" : ""}
                role="tab"
                aria-selected={mode === "login"}
                onClick={() => {
                  setMode("login");
                  setError("");
                }}
              >
                Log in
              </Button>
              <Button
                variant="ghost"
                className={mode === "register" ? "selected" : ""}
                role="tab"
                aria-selected={mode === "register"}
                onClick={() => {
                  setMode("register");
                  setError("");
                }}
              >
                Create an account
              </Button>
            </div>
            {success && (
              <div className="success-notice auth-success" role="status">
                {success}
              </div>
            )}
            <form className="form-stack" onSubmit={submit}>
              {mode === "register" && (
                <>
                  <label>
                    Your name
                    <input
                      name="name"
                      autoComplete="name"
                      required
                      minLength={2}
                      maxLength={100}
                      placeholder="Full name"
                    />
                  </label>
                  <label>
                    Phone number (optional)
                    <input
                      name="phone"
                      type="tel"
                      autoComplete="tel"
                      placeholder="+254 7XX XXX XXX"
                    />
                  </label>
                  <label>
                    I’m here to
                    <select
                      value={role}
                      onChange={(e) => setRole(e.target.value as "customer" | "artisan")}
                    >
                      <option value="customer">Find and book services</option>
                      <option value="artisan">Offer my services</option>
                    </select>
                  </label>
                </>
              )}
              <label>
                Email address
                <input
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  placeholder="you@example.com"
                />
              </label>
              <label>
                Password
                <input
                  name="password"
                  type="password"
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                  required
                  minLength={6}
                  maxLength={50}
                />
              </label>
              {mode === "register" && (
                <span className="form-hint">Use 6–50 characters for your password.</span>
              )}
              {error && (
                <p className="inline-error" role="alert">
                  {error}
                </p>
              )}
              <Button disabled={busy} type="submit" size="lg" data-testid="login-submit-button">
                {busy ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}
                <ArrowRight />
              </Button>
            </form>
          </>
        )}
      </div>
    </main>
  );
}
