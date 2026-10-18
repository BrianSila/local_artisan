import { createFileRoute } from "@tanstack/react-router";
import { OnboardingPage } from "@/components/local/artisan";
import { RoleOnly } from "@/components/local/account";
import { metadata } from "@/lib/local/api";
export const Route = createFileRoute("/_account/onboarding")({
  head: () =>
    metadata(
      "Artisan setup",
      "Complete and manage your artisan introduction, location, and contact details.",
    ),
  component: () => (
    <RoleOnly roles={["artisan"]}>
      <OnboardingPage />
    </RoleOnly>
  ),
});
