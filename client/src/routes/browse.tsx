import { createFileRoute } from "@tanstack/react-router";
import { BrowsePage, type BrowseSearch } from "@/components/local/marketplace";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/browse")({
  validateSearch: (s: Record<string, unknown>): BrowseSearch => ({
    search_term: typeof s["search_term"] === "string" ? s["search_term"] : undefined,
    category_slug: typeof s["category_slug"] === "string" ? s["category_slug"] : undefined,
    county_id: s["county_id"] ? String(s["county_id"]) : undefined,
    sub_county_id: s["sub_county_id"] ? String(s["sub_county_id"]) : undefined,
    page: Math.max(1, Number(s["page"]) || 1),
    latitude:
      s["latitude"] !== undefined &&
      s["longitude"] !== undefined &&
      Number.isFinite(Number(s["latitude"])) &&
      Number.isFinite(Number(s["longitude"]))
        ? Number(s["latitude"])
        : undefined,
    longitude:
      s["latitude"] !== undefined &&
      s["longitude"] !== undefined &&
      Number.isFinite(Number(s["latitude"])) &&
      Number.isFinite(Number(s["longitude"]))
        ? Number(s["longitude"])
        : undefined,
    radius_km:
      s["radius_km"] !== undefined &&
      s["radius_km"] !== "" &&
      Number.isFinite(Number(s["radius_km"]))
        ? Math.min(500, Math.max(1, Number(s["radius_km"])))
        : undefined,
  }),
  head: () =>
    metadata(
      "Find a service",
      "Search local services across Kenya by category, county, and nearby location.",
    ),
  component: Browse,
});
function Browse() {
  return <BrowsePage filters={Route.useSearch()} />;
}
