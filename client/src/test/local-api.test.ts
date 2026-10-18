import { nairobiDate, nairobiLocalToIso } from "@/lib/local/api";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  api,
  ApiError,
  getStoredAuth,
  price,
  queryString,
  storeAuth,
  type User,
} from "@/lib/local/api";

const testUser: User = {
  id: "user-uuid",
  name: "Test User",
  email: "test@example.com",
  role: "customer",
  is_blocked: false,
  created_at: "2026-01-01",
};
afterEach(() => {
  sessionStorage.clear();
  vi.restoreAllMocks();
});
it("treats backend timestamps as UTC and Nairobi-local form values as EAT", () => {
  expect(nairobiLocalToIso("2026-10-17T10:00")).toBe("2026-10-17T07:00:00.000Z");
  expect(nairobiDate("2026-10-17T07:00:00")).toContain("10:00");
});
describe("Flask API client", () => {
  it("attaches the session token and sends the documented JSON body", async () => {
    storeAuth({ access_token: "test-token", user: testUser });
    const fetcher = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(JSON.stringify({ message: "Created" }), { status: 200 }));
    await api("/bookings", {
      method: "POST",
      body: { service_id: "service-uuid" },
    });
    const options = fetcher.mock.calls[0]?.[1];
    expect(new Headers(options?.headers).get("Authorization")).toBe("Bearer test-token");
    expect(options?.body).toBe(JSON.stringify({ service_id: "service-uuid" }));
  });
  it("clears the session on 401 and preserves the API message", async () => {
    storeAuth({ access_token: "expired-test-token", user: testUser });
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ message: "Session expired" }), { status: 401 }),
    );
    await expect(api("/bookings/history")).rejects.toThrow("Session expired");
    expect(getStoredAuth()).toBeNull();
  });
  it("includes field-level validation details from Flask errors", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          error: "Validation failed",
          details: { availability_slot_id: ["Missing data for required field."] },
        }),
        { status: 400 },
      ),
    );
    await expect(api("/bookings", { method: "POST", body: {} })).rejects.toThrow(
      "Validation failed: availability_slot_id: Missing data for required field.",
    );
  });
  it("reports unavailable APIs without fabricating results", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Network unavailable"));
    await expect(api("/marketplace/search")).rejects.toBeInstanceOf(ApiError);
  });
  it("does not set JSON content type for multipart uploads", async () => {
    const fetcher = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("{}"));
    const form = new FormData();
    form.set("bio", "An artisan introduction.");
    await api("/artisan/onboard", { method: "POST", body: form });
    expect(new Headers(fetcher.mock.calls[0]?.[1]?.headers).has("Content-Type")).toBe(false);
  });
  it("omits absent filters and labels negotiated prices honestly", () => {
    expect(queryString({ page: 1, county_id: "", latitude: undefined })).toBe("page=1");
    expect(
      price({
        id: "service-uuid",
        artisan_id: "artisan-uuid",
        category_id: 1,
        title: "Test",
        description: "",
        base_price: 0,
        price_type: "negotiable",
      }),
    ).toBe("Price on discussion");
  });
});
