import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { getStoredAuth } from "@/lib/local/api";
import { AccountLayout } from "@/components/local/account";
export const Route = createFileRoute("/_account")({
  ssr: false,
  beforeLoad: ({ location }) => {
    if (!getStoredAuth()) throw redirect({ to: "/auth", search: { redirect: location.href } });
  },
  component: () => (
    <AccountLayout>
      <Outlet />
    </AccountLayout>
  ),
});
