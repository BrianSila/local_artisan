import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { OnboardingPage } from "@/components/local/artisan";

vi.mock("@/lib/local/auth", () => ({
  useAuth: () => ({ user: { id: "artisan-user", role: "artisan", phone: "+254700000000" } }),
}));

vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}));

afterEach(() => vi.restoreAllMocks());

describe("Returning artisan profile form", () => {
  it("loads the existing profile and pre-fills editable fields", async () => {
    const profile = {
      id: "profile-uuid",
      user_id: "artisan-user",
      name: "Amina Artisan",
      email: "amina@example.test",
      phone: "+254700000000",
      bio: "Experienced electrical repairs and installation services.",
      experience_years: 8,
      primary_phone: "+254711111111",
      profile_image_url: "http://localhost/static/uploads/artisans/amina.jpg",
      is_verified: true,
      county_id: 47,
      county_name: "Nairobi",
      sub_county_id: 18,
      sub_county_name: "Westlands",
      specific_address: "Westlands, Nairobi",
      latitude: -1.26,
      longitude: 36.8,
      work_photos: [],
    };
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.endsWith("/locations/counties")) return Response.json([]);
      if (url.endsWith("/artisan/profile")) return Response.json({ profile });
      throw new Error(`Unexpected request: ${url}`);
    });
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <OnboardingPage />
      </QueryClientProvider>,
    );

    expect(await screen.findByDisplayValue(profile.bio)).toBeInTheDocument();
    expect(screen.getByDisplayValue(profile.primary_phone)).toBeInTheDocument();
    expect(screen.getByDisplayValue(profile.specific_address)).toBeInTheDocument();
    expect(screen.getByDisplayValue(String(profile.latitude))).toBeInTheDocument();
    expect(screen.getByDisplayValue(String(profile.longitude))).toBeInTheDocument();
    expect(
      screen.getByText((_, element) => {
        const hasText = /8\s+years of experience\s+·\s+Nairobi,\s*Westlands/.test(
          element?.textContent || "",
        );
        return hasText && element?.tagName.toLowerCase() === "p";
      }),
    ).toBeInTheDocument();
  });
});
