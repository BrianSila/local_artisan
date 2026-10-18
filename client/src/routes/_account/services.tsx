import { createFileRoute } from "@tanstack/react-router";
import { ServicesPage } from "@/components/local/artisan";
import { RoleOnly } from "@/components/local/account";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/_account/services")({
  head: () => metadata("My services", "Add and manage your Local Artisan service catalog."),
  component: () => (
    <RoleOnly roles={["artisan"]}>
      <ServicesPage />
    </RoleOnly>
  ),
});
