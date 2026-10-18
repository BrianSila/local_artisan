import { createFileRoute } from "@tanstack/react-router";
import { AboutPage } from "@/components/local/home";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/about")({
  head: () =>
    metadata(
      "Our story",
      "Meet Local Artisan, connecting Kenyan communities with local skills and services.",
    ),
  component: AboutPage,
});
