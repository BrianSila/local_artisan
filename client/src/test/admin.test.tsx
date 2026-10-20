import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AdminPage } from "@/components/local/admin";

afterEach(() => vi.restoreAllMocks());

function renderAdmin() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <AdminPage />
    </QueryClientProvider>,
  );
}

describe("Admin record summaries", () => {
  it("resolves artisan location IDs to county and sub-county names", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.endsWith("/admin/dashboard/stats")) return Response.json({});
      if (url.endsWith("/admin/artisans/pending?page=1&limit=10"))
        return Response.json({
          total: 1,
          page: 1,
          pages: 1,
          items: [
            {
              id: "profile-uuid",
              user_id: "user-uuid",
              name: "Amina Artisan",
              email: "amina@example.test",
              primary_phone: "+254700000000",
              bio: "Electrical repairs for homes.",
              experience_years: 8,
              county_id: 47,
              sub_county_id: 18,
              specific_address: "Westlands",
              latitude: null,
              longitude: null,
              profile_image: null,
            },
          ],
        });
      if (url.endsWith("/locations/counties"))
        return Response.json([
          { id: 47, name: "Nairobi", sub_counties: [{ id: 18, name: "Westlands" }] },
        ]);
      throw new Error(`Unexpected request: ${url}`);
    });

    renderAdmin();

    expect(await screen.findByText("Nairobi · Westlands")).toBeInTheDocument();
    expect(screen.queryByText("County #47 · Subcounty #18")).not.toBeInTheDocument();
  });

  it("renders disputes as labeled summaries with readable statuses", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.endsWith("/admin/dashboard/stats")) return Response.json({});
      if (url.endsWith("/admin/artisans/pending?page=1&limit=10"))
        return Response.json({ total: 0, page: 1, pages: 0, items: [] });
      if (url.endsWith("/locations/counties")) return Response.json([]);
      if (url.endsWith("/admin/disputes?page=1&limit=10"))
        return Response.json({
          total: 1,
          page: 1,
          pages: 1,
          items: [
            {
              id: 7,
              booking_id: "12345678-1234-1234-1234-123456789abc",
              raised_by: "87654321-4321-4321-4321-cba987654321",
              reason: "The agreed work was not completed.",
              status: "open",
              resolution_details: null,
              created_at: "2026-10-17T07:00:00",
            },
          ],
        });
      throw new Error(`Unexpected request: ${url}`);
    });

    renderAdmin();
    fireEvent.click(screen.getByRole("tab", { name: "Open disputes" }));

    expect(await screen.findByRole("heading", { name: "Dispute #7" })).toBeInTheDocument();
    expect(screen.getByText("Open")).toBeInTheDocument();
    expect(screen.getByText("Reason")).toBeInTheDocument();
    expect(screen.getByText("The agreed work was not completed.")).toBeInTheDocument();
    expect(screen.getByText("Booking ID")).toBeInTheDocument();
    expect(screen.getByText("Raised by account")).toBeInTheDocument();
    expect(screen.queryByText("booking_id:", { exact: false })).not.toBeInTheDocument();
  });
});
