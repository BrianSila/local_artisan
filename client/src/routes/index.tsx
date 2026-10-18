import { createFileRoute } from "@tanstack/react-router";
import { HomePage } from "@/components/local/home";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/")({
  head: () =>
    metadata(
      "Local skills. Real connections.",
      "Find local services, request bookings, and connect with skilled artisans across Kenya.",
    ),
  component: HomePage,
});
