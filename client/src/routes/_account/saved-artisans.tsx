import { createFileRoute } from "@tanstack/react-router";
import { SavedArtisansPage } from "@/components/local/artisan-profile";
import { metadata } from "@/lib/local/api";

export const Route = createFileRoute("/_account/saved-artisans")({
  head: () => metadata("Saved artisans", "Revisit your saved Local Artisan profiles."),
  component: SavedArtisansPage,
});
