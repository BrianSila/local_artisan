import { createFileRoute } from "@tanstack/react-router";
import { ArtisanProfilePage } from "@/components/local/artisan-profile";
import { metadata } from "@/lib/local/api";

export const Route = createFileRoute("/artisans/$id")({
  head: () =>
    metadata("Artisan profile", "Explore an artisan’s profile, services, work, and reviews."),
  component: ArtisanProfileRoute,
});

function ArtisanProfileRoute() {
  return <ArtisanProfilePage id={Route.useParams().id} />;
}
