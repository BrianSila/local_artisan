import { createFileRoute } from "@tanstack/react-router";
import { AdminPage } from "@/components/local/admin";
import { RoleOnly } from "@/components/local/account";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/_account/admin")({
  head: () =>
    metadata("Community administration", "Manage artisan verification, users, and open disputes."),
  component: () => (
    <RoleOnly roles={["admin"]}>
      <AdminPage />
    </RoleOnly>
  ),
});
