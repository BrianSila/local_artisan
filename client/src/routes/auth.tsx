import { createFileRoute } from "@tanstack/react-router";
import { AuthPage, type AuthSearch } from "@/components/local/auth-page";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/auth")({
  validateSearch: (s: Record<string, unknown>): AuthSearch => ({
    mode: s["mode"] === "register" ? "register" : "login",
    role: s["role"] === "artisan" ? "artisan" : "customer",
    redirect:
      typeof s["redirect"] === "string" &&
      s["redirect"].startsWith("/") &&
      !s["redirect"].startsWith("//") &&
      !s["redirect"].includes("\\")
        ? s["redirect"]
        : undefined,
  }),
  head: () =>
    metadata(
      "Your account",
      "Log in or join Local Artisan to book services and share your skills.",
    ),
  component: Auth,
});
function Auth() {
  return <AuthPage search={Route.useSearch()} />;
}
