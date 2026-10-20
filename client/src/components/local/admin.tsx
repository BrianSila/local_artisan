import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  api,
  nairobiDate,
  type Dispute,
  type Location,
  type Page,
  type PendingArtisan,
  type User,
  type UUID,
} from "@/lib/local/api";
import { MapPin } from "lucide-react";
import { Empty, ErrorNotice, Loading, Pagination } from "./shared";
interface Stats {
  total_users: number;
  total_artisans: number;
  verified_artisans: number;
  active_disputes: number;
}
type Change =
  | { kind: "verify"; id: UUID; name: string }
  | { kind: "suspend"; id: UUID; name: string; blocked: boolean }
  | { kind: "role"; id: UUID; name: string; role: User["role"] }
  | { kind: "resolve"; id: number; name: string };

function readableStatus(status: string) {
  return status.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function shortReference(value: string) {
  return `${value.slice(0, 8)}…`;
}

export function AdminPage() {
  const [tab, setTab] = useState<"artisans" | "disputes" | "users">("artisans");
  const [page, setPage] = useState(1);
  const [change, setChange] = useState<Change | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const query = useQueryClient();
  const stats = useQuery({
    queryKey: ["admin-stats"],
    queryFn: () => api<Stats>("/admin/dashboard/stats"),
    retry: false,
  });
  const artisans = useQuery({
    queryKey: ["admin-artisans", page],
    queryFn: () => api<Page<PendingArtisan>>(`/admin/artisans/pending?page=${page}&limit=10`),
    enabled: tab === "artisans",
    retry: false,
  });
  const counties = useQuery({
    queryKey: ["counties"],
    queryFn: ({ signal }) => api<Location[]>("/locations/counties", { signal }),
    enabled: tab === "artisans",
    staleTime: 300000,
    retry: false,
  });
  const disputes = useQuery({
    queryKey: ["admin-disputes", page],
    queryFn: () => api<Page<Dispute>>(`/admin/disputes?page=${page}&limit=10`),
    enabled: tab === "disputes",
    retry: false,
  });
  const users = useQuery({
    queryKey: ["admin-users", page],
    queryFn: () => api<Page<User>>(`/auth/users?page=${page}&limit=10`),
    enabled: tab === "users",
    retry: false,
  });
  const current = tab === "artisans" ? artisans : tab === "disputes" ? disputes : users;
  function select(value: Change) {
    setChange(value);
    setError("");
    setSuccess("");
  }
  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!change) return;
    setBusy(true);
    setError("");
    const f = new FormData(e.currentTarget);
    try {
      const path =
        change.kind === "verify"
          ? `/admin/artisans/${change.id}/verify`
          : change.kind === "suspend"
            ? `/admin/users/${change.id}/suspend`
            : change.kind === "role"
              ? `/auth/users/${change.id}/role`
              : `/admin/disputes/${encodeURIComponent(change.id)}/resolve`;
      const body =
        change.kind === "verify"
          ? { is_verified: true }
          : change.kind === "suspend"
            ? { is_blocked: !change.blocked }
            : change.kind === "role"
              ? { role: String(f.get("role")) }
              : {
                  resolution_status: String(f.get("resolution_status")),
                  resolution_details: String(f.get("resolution_details")),
                };
      const result = await api<{ message?: string }>(path, {
        method: change.kind === "resolve" ? "POST" : "PATCH",
        body,
      });
      setSuccess(result.message || "The action has been saved.");
      await Promise.all([
        query.invalidateQueries({ queryKey: ["admin-stats"] }),
        query.invalidateQueries({ queryKey: ["admin-artisans"] }),
        query.invalidateQueries({ queryKey: ["admin-disputes"] }),
        query.invalidateQueries({ queryKey: ["admin-users"] }),
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Action unsuccessful.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <h1 className="page-title">Community administration</h1>
      <p className="page-subtitle">Support artisans, manage accounts, and resolve open issues.</p>
      {stats.isLoading ? (
        <Loading />
      ) : stats.error ? (
        <ErrorNotice error={stats.error} retry={() => stats.refetch()} />
      ) : (
        stats.data && (
          <div className="stats-grid">
            {[
              { label: "Total users", value: stats.data.total_users },
              { label: "Artisans", value: stats.data.total_artisans },
              { label: "Verified artisans", value: stats.data.verified_artisans },
              { label: "Active disputes", value: stats.data.active_disputes },
            ].map((s) => (
              <div key={s.label} className="stat">
                <p>{s.label}</p>
                <strong>{s.value}</strong>
              </div>
            ))}
          </div>
        )
      )}
      <div className="segmented admin-tabs" role="tablist" aria-label="Administration sections">
        {(["artisans", "disputes", "users"] as const).map((t) => (
          <Button
            key={t}
            variant="ghost"
            className={t === tab ? "selected" : ""}
            role="tab"
            aria-selected={t === tab}
            onClick={() => {
              setTab(t);
              setPage(1);
            }}
          >
            {t === "artisans" ? "Pending artisans" : t === "disputes" ? "Open disputes" : "Users"}
          </Button>
        ))}
      </div>
      {current.isLoading ? (
        <Loading />
      ) : current.error ? (
        <ErrorNotice error={current.error} retry={() => current.refetch()} />
      ) : !current.data?.items.length ? (
        <Empty
          title={
            tab === "artisans"
              ? "No pending artisans"
              : tab === "disputes"
                ? "No open disputes"
                : "No users found"
          }
        />
      ) : (
        <>
          {tab === "artisans" && (
            <>
              {counties.error && (
                <ErrorNotice error={counties.error} retry={() => counties.refetch()} />
              )}
              {artisans.data?.items.map((a) => {
                const county = counties.data?.find((item) => item.id === a.county_id);
                const subCounty = county?.sub_counties?.find((item) => item.id === a.sub_county_id);
                const location =
                  county && subCounty
                    ? `${county.name} · ${subCounty.name}`
                    : counties.isLoading
                      ? "Loading location names…"
                      : "Location unavailable";
                return (
                  <article key={a.id} className="booking-row">
                    <div>
                      <h3>{a.name}</h3>
                      <p>
                        {a.email} · {a.primary_phone}
                      </p>
                      <p>
                        {a.experience_years} years of experience · {a.specific_address}
                      </p>
                      <p className="admin-artisan-location">
                        <MapPin size={14} /> {location}
                      </p>
                      {a.bio && <p>{a.bio}</p>}
                    </div>
                    <Button onClick={() => select({ kind: "verify", id: a.id, name: a.name })}>
                      Verify artisan
                    </Button>
                  </article>
                );
              })}
            </>
          )}
          {tab === "users" &&
            users.data?.items.map((u) => (
              <article key={u.id} className="booking-row admin-user-row">
                <div className="admin-user-summary">
                  <h3>
                    {u.name} <span className="status admin-role-badge">{u.role}</span>
                  </h3>
                  <div className="admin-user-meta">
                    <p>
                      {u.email} · {u.phone || "No phone provided"}
                    </p>
                    <span
                      className={`status ${u.is_blocked ? "status-disputed" : "status-accepted"}`}
                    >
                      {u.is_blocked ? "Suspended" : "Active"}
                    </span>
                  </div>
                </div>
                <div className="row-actions">
                  <Button
                    variant="outline"
                    onClick={() => select({ kind: "role", id: u.id, name: u.name, role: u.role })}
                  >
                    Change role
                  </Button>
                  {u.role !== "admin" && (
                    <Button
                      variant="outline"
                      onClick={() =>
                        select({ kind: "suspend", id: u.id, name: u.name, blocked: u.is_blocked })
                      }
                    >
                      {u.is_blocked ? "Restore access" : "Suspend"}
                    </Button>
                  )}
                </div>
              </article>
            ))}
          {tab === "disputes" &&
            disputes.data?.items.map((d) => (
              <article className="booking-row admin-dispute-row" key={d.id}>
                <div>
                  <div className="admin-record-heading">
                    <h3>Dispute #{d.id}</h3>
                    <span className="status">{readableStatus(d.status)}</span>
                  </div>
                  <dl className="admin-dispute-summary">
                    <div>
                      <dt>Reason</dt>
                      <dd>{d.reason}</dd>
                    </div>
                    <div>
                      <dt>Booking ID</dt>
                      <dd title={d.booking_id}>
                        <code>{shortReference(d.booking_id)}</code>
                      </dd>
                    </div>
                    <div>
                      <dt>Raised by account</dt>
                      <dd title={d.raised_by}>
                        <code>{shortReference(d.raised_by)}</code>
                      </dd>
                    </div>
                    <div>
                      <dt>Filed</dt>
                      <dd>
                        <time dateTime={d.created_at}>{nairobiDate(d.created_at)}</time>
                      </dd>
                    </div>
                    {d.resolution_details && (
                      <div>
                        <dt>Resolution details</dt>
                        <dd>{d.resolution_details}</dd>
                      </div>
                    )}
                  </dl>
                </div>
                <Button
                  onClick={() => select({ kind: "resolve", id: d.id, name: `Dispute #${d.id}` })}
                >
                  Resolve dispute
                </Button>
              </article>
            ))}
          <Pagination page={page} pages={current.data?.pages || 0} onPage={setPage} />
        </>
      )}
      <Dialog
        open={!!change}
        onOpenChange={(open) => {
          if (!open && !busy) setChange(null);
        }}
      >
        <DialogContent className="admin-action-dialog">
          <DialogTitle className="admin-action-title">
            {change?.kind === "verify"
              ? "Verify artisan"
              : change?.kind === "suspend"
                ? change.blocked
                  ? "Restore account access"
                  : "Suspend account"
                : change?.kind === "role"
                  ? "Change account role"
                  : "Resolve dispute"}
          </DialogTitle>
          <DialogDescription className="admin-action-description">
            {change?.name} · Confirm this change before continuing.
          </DialogDescription>
          <form className="admin-action-form form-stack" onSubmit={submit}>
            {!success && (
              <>
                {change?.kind === "role" && (
                  <label>
                    Role
                    <select name="role" defaultValue={change.role}>
                      <option value="customer">Customer</option>
                      <option value="artisan">Artisan</option>
                      <option value="admin">Administrator</option>
                    </select>
                  </label>
                )}
                {change?.kind === "resolve" && (
                  <>
                    <label>
                      Resolution
                      <select name="resolution_status">
                        <option value="released_to_fundi">Release to artisan</option>
                        <option value="refunded">Refund</option>
                      </select>
                    </label>
                    <label>
                      Resolution details
                      <textarea
                        name="resolution_details"
                        required
                        minLength={10}
                        maxLength={2000}
                      />
                    </label>
                  </>
                )}
                {error && (
                  <p className="inline-error" role="alert">
                    {error}
                  </p>
                )}
                <div className="admin-action-actions form-actions">
                  <Button disabled={busy} type="submit">
                    {busy ? "Saving…" : "Confirm change"}
                  </Button>
                  <Button
                    variant="ghost"
                    type="button"
                    disabled={busy}
                    onClick={() => setChange(null)}
                  >
                    Cancel
                  </Button>
                </div>
              </>
            )}
            {success && (
              <>
                <p className="success-notice" role="status">
                  {success}
                </p>
                <Button className="admin-action-done" type="button" onClick={() => setChange(null)}>
                  Done
                </Button>
              </>
            )}
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
