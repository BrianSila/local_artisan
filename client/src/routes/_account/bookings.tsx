import { createFileRoute } from "@tanstack/react-router";
import { BookingsPage } from "@/components/local/bookings";
import { RoleOnly } from "@/components/local/account";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/_account/bookings")({
  head: () =>
    metadata("My bookings", "Track your service requests and manage bookings on Local Artisan."),
  component: () => (
    <RoleOnly roles={["customer", "artisan"]}>
      <BookingsPage />
    </RoleOnly>
  ),
});
