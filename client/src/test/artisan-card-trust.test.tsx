import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ArtisanCard } from "@/components/local/artisan-card";
import type { Service } from "@/lib/local/api";

vi.mock("@/lib/local/auth", () => ({ useAuth: () => ({ user: null }) }));

vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}));

const service: Service = {
  id: "service-uuid",
  artisan_id: "artisan-uuid",
  category_id: 3,
  title: "Home wiring repair",
  description: "Diagnosis and repair for home electrical wiring.",
  price_type: "fixed",
  base_price: 2500,
  artisan_name: "Amina Artisan",
  artisan_photo_url: "https://api.example.test/static/amina.jpg",
  is_verified: true,
  specialty: "Electrician",
  county_name: "Nairobi",
  sub_county_name: "Westlands",
  average_rating: 4.5,
  review_count: 8,
  completed_job_count: 12,
};

describe("Marketplace artisan trust details", () => {
  it("shows artisan identity, verification, location, and server-calculated stats", () => {
    render(<ArtisanCard service={service} category={undefined} />);

    expect(screen.getByRole("heading", { name: "Home wiring repair" })).toBeInTheDocument();
    expect(screen.getByText("Amina Artisan")).toBeInTheDocument();
    expect(screen.getByText("Verified artisan")).toBeInTheDocument();
    expect(screen.getByText("Nairobi · Westlands")).toBeInTheDocument();
    expect(screen.getByText("4.5 (8 reviews)")).toBeInTheDocument();
    expect(screen.getByText("12 completed jobs")).toBeInTheDocument();
    expect(screen.getByAltText(/Amina Artisan/i)).toHaveAttribute("src", service.artisan_photo_url);
  });

  it("does not invent a rating when the artisan has no reviews", () => {
    render(
      <ArtisanCard
        service={{ ...service, average_rating: null, review_count: 0, completed_job_count: 0 }}
        category={undefined}
      />,
    );

    expect(screen.getByText("No reviews yet")).toBeInTheDocument();
    expect(screen.queryByText(/0\.0/)).not.toBeInTheDocument();
  });
});
