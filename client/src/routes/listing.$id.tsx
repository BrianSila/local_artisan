import { createFileRoute } from "@tanstack/react-router";
import { ListingPage } from "@/components/local/marketplace";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/listing/$id")({
  head: ({ params }) =>
    metadata(
      `Service ${params.id}`,
      "Explore this local service, request a booking, and contact the artisan.",
    ),
  component: Listing,
});
function Listing() {
  return <ListingPage id={Route.useParams().id} />;
}
