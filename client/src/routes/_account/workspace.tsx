import { createFileRoute } from "@tanstack/react-router";
import { AccountPage } from "@/components/local/account";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/_account/workspace")({
  head: () => metadata("My account", "Manage your Local Artisan account and personal details."),
  component: AccountPage,
});
