import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AuthPage } from "@/components/local/auth-page";

const navigateMock = vi.hoisted(() => vi.fn());

vi.mock("@/lib/local/auth", () => ({
  useAuth: () => ({ user: null, setSession: vi.fn() }),
}));

vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
  useNavigate: () => navigateMock,
}));

afterEach(() => {
  vi.restoreAllMocks();
  navigateMock.mockReset();
});

async function submitArtisanLogin(profileStatus: number) {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const url = String(input);
    if (url.endsWith("/auth/login"))
      return Response.json({
        message: "Login successful",
        access_token: "artisan-token",
        user: {
          id: "artisan-user",
          name: "Amina Artisan",
          email: "amina@example.test",
          role: "artisan",
          is_blocked: false,
          created_at: "2026-10-17T07:00:00",
        },
      });
    if (url.endsWith("/artisan/profile"))
      return Response.json(
        profileStatus === 404 ? { error: "Artisan profile not found" } : { profile: {} },
        { status: profileStatus },
      );
    throw new Error(`Unexpected request: ${url}`);
  });

  render(<AuthPage search={{ mode: "login" }} />);
  fireEvent.change(screen.getByLabelText("Email address"), {
    target: { value: "amina@example.test" },
  });
  fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secret123" } });
  fireEvent.click(screen.getByTestId("login-submit-button"));
  await waitFor(() => expect(navigateMock).toHaveBeenCalled());
}

describe("Artisan login redirect", () => {
  it("sends artisans with an existing profile to the workspace", async () => {
    await submitArtisanLogin(200);

    expect(navigateMock).toHaveBeenCalledWith({ to: "/workspace" });
  });

  it("sends artisans without a profile to onboarding", async () => {
    await submitArtisanLogin(404);

    expect(navigateMock).toHaveBeenCalledWith({ to: "/onboarding" });
  });
});
