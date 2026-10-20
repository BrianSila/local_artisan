import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { Trash2, Plus, ArrowRight, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import {
  ApiError,
  api,
  nairobiDate,
  nairobiLocalToIso,
  price,
  type AvailabilitySlot,
  type Profile,
  type Service,
} from "@/lib/local/api";
import { Empty, ErrorNotice, Loading, LocationFields, useCategories } from "./shared";
import { useAuth } from "@/lib/local/auth";

interface ArtisanProfileDetails extends Profile {
  experience_years?: number;
  county_id?: number;
  county_name?: string;
  sub_county_id?: number;
  sub_county_name?: string;
  latitude?: number | null;
  longitude?: number | null;
  profile_image_url?: string | null;
}

export function OnboardingPage() {
  const [county, setCounty] = useState("");
  const [sub, setSub] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const query = useQueryClient();
  const { user } = useAuth();
  const profileQuery = useQuery({
    queryKey: ["artisan-profile"],
    queryFn: ({ signal }) =>
      api<{ profile: ArtisanProfileDetails }>("/artisan/profile", { signal }),
    retry: false,
  });
  const profile = profileQuery.data?.profile ?? null;
  const editing = profile !== null;

  if (profileQuery.isLoading) return <Loading />;
  if (
    profileQuery.error &&
    !(profileQuery.error instanceof ApiError && profileQuery.error.status === 404)
  ) {
    return <ErrorNotice error={profileQuery.error} retry={() => profileQuery.refetch()} />;
  }
  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setSuccess("");
    const f = new FormData(e.currentTarget);
    const image = f.get("profile_image");
    if (image instanceof File && image.size > 5 * 1024 * 1024) {
      setError("Your photo must be no larger than 5 MB.");
      return;
    }
    const lat = String(f.get("latitude") || "");
    const lng = String(f.get("longitude") || "");
    if (Boolean(lat) !== Boolean(lng)) {
      setError("Please provide both latitude and longitude, or leave both blank.");
      return;
    }
    setBusy(true);
    try {
      if (editing) {
        const body = {
          bio: String(f.get("bio")),
          primary_phone: String(f.get("primary_phone")),
          specific_address: String(f.get("specific_address")),
          ...(lat && lng ? { latitude: Number(lat), longitude: Number(lng) } : {}),
        };
        const result = await api<{ message: string; profile: Profile }>("/artisan/profile", {
          method: "PUT",
          body,
        });
        await profileQuery.refetch();
        setSuccess(result.message || "Your artisan profile has been updated.");
      } else {
        f.set("county_id", county);
        f.set("sub_county_id", sub);
        if (!lat) {
          f.delete("latitude");
          f.delete("longitude");
        }
        if (!(image instanceof File) || !image.size) f.delete("profile_image");
        const result = await api<{ message: string; profile: Profile }>("/artisan/onboard", {
          method: "POST",
          body: f,
        });
        await profileQuery.refetch();
        setSuccess(result.message || "Your artisan profile is ready.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Setup unsuccessful.");
    } finally {
      setBusy(false);
    }
  }
  async function upload(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const image = f.get("profile_image");
    setError("");
    setSuccess("");
    if (!(image instanceof File) || !image.size || image.size > 5 * 1024 * 1024) {
      setError("Choose a photo no larger than 5 MB.");
      return;
    }
    setBusy(true);
    try {
      const r = await api<{ message: string; profile_image_url: string }>(
        "/artisan/profile/image",
        { method: "PUT", body: f },
      );
      await profileQuery.refetch();
      setSuccess(r.message || "Profile photo updated.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload unsuccessful.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <h1 className="page-title">{editing ? "Your artisan profile" : "Make your skills known."}</h1>
      <p className="page-subtitle">
        {editing
          ? "Keep your contact details and introduction up to date."
          : "Introduce yourself and tell your community where to find you."}
      </p>
      {editing && (
        <p className="form-hint artisan-profile-meta">
          {profile.experience_years ?? 0} years of experience ·{" "}
          {profile.county_name || "Location pending"}
          {profile.sub_county_name ? `, ${profile.sub_county_name}` : ""}
        </p>
      )}
      <form key={editing ? "edit" : "setup"} className="artisan-form form-stack" onSubmit={submit}>
        <label>
          About you
          <textarea
            name="bio"
            required
            minLength={10}
            maxLength={1000}
            defaultValue={profile?.bio || ""}
            placeholder="Your skills, your approach, and what you love about your work…"
          />
        </label>
        <div className="form-grid">
          {!editing && (
            <label>
              Years of experience
              <input
                name="experience_years"
                type="number"
                required
                min={0}
                max={50}
                defaultValue={0}
              />
            </label>
          )}
          <label>
            Primary phone number
            <input
              name="primary_phone"
              type="tel"
              required
              minLength={10}
              maxLength={15}
              defaultValue={profile?.primary_phone || user?.phone || ""}
              placeholder="+254712345678"
            />
          </label>
          {!editing && (
            <LocationFields
              county={county}
              subcounty={sub}
              onCounty={setCounty}
              onSubcounty={setSub}
              required
            />
          )}
        </div>
        <label>
          Specific address
          <input
            name="specific_address"
            required
            minLength={2}
            maxLength={255}
            defaultValue={profile?.specific_address || ""}
            placeholder="Street, estate, or a nearby landmark"
          />
        </label>
        {editing && profile.profile_image_url && (
          <img
            className="artisan-profile-preview"
            src={profile.profile_image_url}
            alt={`${user?.name || "Your"} artisan profile`}
          />
        )}
        <div className="form-grid">
          <label>
            Latitude (optional)
            <input
              name="latitude"
              type="number"
              step="any"
              min={-90}
              max={90}
              defaultValue={profile?.latitude ?? ""}
            />
          </label>
          <label>
            Longitude (optional)
            <input
              name="longitude"
              type="number"
              step="any"
              min={-180}
              max={180}
              defaultValue={profile?.longitude ?? ""}
            />
          </label>
        </div>
        <span className="form-hint">Provide both coordinates, or leave both blank.</span>
        {!editing && (
          <label>
            Profile photo (optional, up to 5 MB)
            <input type="file" name="profile_image" accept="image/*" />
          </label>
        )}
        {error && (
          <p className="inline-error" role="alert">
            {error}
          </p>
        )}
        {success && (
          <div className="success-notice" role="status">
            {success}
            <Link className="text-link onboarding-services-link" to="/services">
              Manage my services <ArrowRight size={15} />
            </Link>
          </div>
        )}
        <Button type="submit" disabled={busy}>
          {busy ? "Saving…" : editing ? "Save profile" : "Complete artisan setup"}
        </Button>
      </form>
      {editing && (
        <form className="artisan-form form-section form-stack" onSubmit={upload}>
          <h2>Your profile photo</h2>
          <label>
            Choose a photo (up to 5 MB)
            <input name="profile_image" required type="file" accept="image/*" />
          </label>
          <Button disabled={busy} type="submit">
            Update photo
          </Button>
        </form>
      )}
    </>
  );
}
export function ServicesPage() {
  const query = useQueryClient();
  const categories = useCategories();
  const availability = useQuery({
    queryKey: ["artisan-availability"],
    queryFn: ({ signal }) => api<AvailabilitySlot[]>("/bookings/availability", { signal }),
    retry: false,
  });
  const services = useQuery({
    queryKey: ["artisan-services"],
    queryFn: ({ signal }) => api<Service[]>("/artisan/services", { signal }),
    retry: false,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [deleting, setDeleting] = useState<Service | null>(null);
  const [editing, setEditing] = useState<Service | null>(null);
  const [priceType, setPriceType] = useState<Service["price_type"]>("fixed");
  const serviceEditorRef = useRef<HTMLElement>(null);
  const [slotBusy, setSlotBusy] = useState(false);
  const [slotError, setSlotError] = useState("");
  const [slotSuccess, setSlotSuccess] = useState("");
  useEffect(() => {
    if (editing) {
      serviceEditorRef.current?.scrollIntoView?.({ behavior: "smooth", block: "start" });
    }
  }, [editing]);
  async function saveService(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const f = new FormData(form);
    const serviceBeingEdited = editing;
    setError("");
    setSuccess("");
    setBusy(true);
    try {
      const r = await api<{ message: string; service: Service }>(
        serviceBeingEdited ? `/artisan/services/${serviceBeingEdited.id}` : "/artisan/services",
        {
          method: serviceBeingEdited ? "PUT" : "POST",
          body: {
            category_id: Number(f.get("category_id")),
            title: String(f.get("title")).trim(),
            description: String(f.get("description")).trim(),
            price_type: priceType,
            base_price: Number(f.get("base_price")),
          },
        },
      );
      setSuccess(r.message || (serviceBeingEdited ? "Service updated." : "Service added."));
      form.reset();
      setEditing(null);
      setPriceType("fixed");
      await query.invalidateQueries({ queryKey: ["artisan-services"] });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to add service.");
    } finally {
      setBusy(false);
    }
  }
  function editService(service: Service) {
    setError("");
    setSuccess("");
    setPriceType(service.price_type);
    setEditing(service);
  }
  function cancelEdit() {
    setError("");
    setSuccess("");
    setPriceType("fixed");
    setEditing(null);
  }
  async function remove() {
    if (!deleting) return;
    setBusy(true);
    setError("");
    try {
      await api(`/artisan/services/${deleting.id}`, { method: "DELETE" });
      setDeleting(null);
      await query.invalidateQueries({ queryKey: ["artisan-services"] });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to delete service.");
    } finally {
      setBusy(false);
    }
  }
  async function addAvailability(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    setSlotError("");
    setSlotSuccess("");
    setSlotBusy(true);
    try {
      const result = await api<{ message?: string; slot: AvailabilitySlot }>(
        "/bookings/availability",
        {
          method: "POST",
          body: {
            starts_at: nairobiLocalToIso(String(data.get("starts_at"))),
            ends_at: nairobiLocalToIso(String(data.get("ends_at"))),
          },
        },
      );
      setSlotSuccess("Availability added.");
      form.reset();
      await query.invalidateQueries({ queryKey: ["artisan-availability"] });
      await query.invalidateQueries({ queryKey: ["artisan-availability", result.slot.artisan_id] });
    } catch (e) {
      setSlotError(e instanceof Error ? e.message : "Unable to add availability.");
    } finally {
      setSlotBusy(false);
    }
  }
  async function removeAvailability(slot: AvailabilitySlot) {
    setSlotError("");
    setSlotSuccess("");
    setSlotBusy(true);
    try {
      await api(`/bookings/availability/${slot.id}`, { method: "DELETE" });
      setSlotSuccess("Availability removed.");
      await query.invalidateQueries({ queryKey: ["artisan-availability"] });
      await query.invalidateQueries({ queryKey: ["artisan-availability", slot.artisan_id] });
    } catch (e) {
      setSlotError(e instanceof Error ? e.message : "Unable to remove availability.");
    } finally {
      setSlotBusy(false);
    }
  }
  return (
    <>
      <h1 className="page-title">Your skills, on show.</h1>
      <p className="page-subtitle">Build a service catalog that reflects what you do best.</p>
      {services.isLoading ? (
        <Loading />
      ) : services.error ? (
        <ErrorNotice error={services.error} retry={() => services.refetch()} />
      ) : services.data?.length ? (
        <div className="service-grid">
          {services.data.map((s) => (
            <article
              className={
                editing?.id === s.id ? "service-card service-card-editing" : "service-card"
              }
              key={s.id}
            >
              <h3>{s.title}</h3>
              <p>{s.description}</p>
              <div className="service-card-footer">
                <strong>{price(s)}</strong>
                <div className="row-actions">
                  <Button
                    variant="ghost"
                    size="icon"
                    title={`Edit ${s.title}`}
                    aria-label={`Edit ${s.title}`}
                    onClick={() => editService(s)}
                  >
                    <Pencil />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    title={`Delete ${s.title}`}
                    aria-label={`Delete ${s.title}`}
                    onClick={() => {
                      setDeleting(s);
                      setError("");
                    }}
                  >
                    <Trash2 />
                  </Button>
                </div>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <Empty title="Your catalog starts here">Add your first service below.</Empty>
      )}
      <section className="artisan-form form-section artisan-form-section">
        <h2>Appointment availability</h2>
        <p className="form-hint">Times are entered and displayed in Nairobi time (EAT).</p>
        {availability.isLoading ? (
          <Loading />
        ) : availability.error ? (
          <ErrorNotice error={availability.error} retry={() => availability.refetch()} />
        ) : availability.data?.length ? (
          <ul className="availability-list">
            {availability.data.map((slot) => (
              <li key={slot.id}>
                <span>
                  {nairobiDate(slot.starts_at)} – {nairobiDate(slot.ends_at)}
                  <small>{slot.status}</small>
                </span>
                {slot.status === "available" && (
                  <Button
                    variant="ghost"
                    size="icon"
                    title="Remove availability"
                    aria-label="Remove availability"
                    disabled={slotBusy}
                    onClick={() => removeAvailability(slot)}
                  >
                    <Trash2 />
                  </Button>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="form-hint">No appointment times published yet.</p>
        )}
        <form className="form-stack availability-form" onSubmit={addAvailability}>
          <div className="form-grid">
            <label>
              Starts at (Nairobi time)
              <input name="starts_at" type="datetime-local" required />
            </label>
            <label>
              Ends at (Nairobi time)
              <input name="ends_at" type="datetime-local" required />
            </label>
          </div>
          {slotError && (
            <p role="alert" className="inline-error">
              {slotError}
            </p>
          )}
          {slotSuccess && (
            <p role="status" className="success-notice">
              {slotSuccess}
            </p>
          )}
          <Button disabled={slotBusy} type="submit">
            <Plus /> {slotBusy ? "Saving…" : "Add appointment time"}
          </Button>
        </form>
      </section>
      <section
        className="artisan-form form-section artisan-form-section"
        id="service-editor"
        ref={serviceEditorRef}
      >
        <h2>{editing ? `Edit ${editing.title}` : "Add a service"}</h2>
        <form key={editing?.id || "new-service"} className="form-stack" onSubmit={saveService}>
          <label>
            Service title
            <input
              name="title"
              required
              minLength={3}
              maxLength={150}
              defaultValue={editing?.title || ""}
              placeholder="What service do you offer?"
            />
          </label>
          <label>
            Category
            <select name="category_id" required defaultValue={editing?.category_id || ""}>
              <option value="">Choose a category</option>
              {categories.data?.map((c) => (
                <option value={c.id} key={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          {categories.error && (
            <ErrorNotice error={categories.error} retry={() => categories.refetch()} />
          )}
          <label>
            Description
            <textarea
              name="description"
              required
              minLength={10}
              maxLength={1000}
              defaultValue={editing?.description || ""}
              placeholder="Describe what’s included in your service…"
            />
          </label>
          <div className="form-grid">
            <label>
              Pricing
              <select value={priceType} onChange={(e) => setPriceType(e.target.value)}>
                <option value="fixed">Fixed price</option>
                <option value="hourly">Hourly</option>
                <option value="negotiable">Negotiable</option>
              </select>
            </label>
            <label>
              Base price (KES)
              <input
                name="base_price"
                type="number"
                min={0}
                step="0.01"
                required
                defaultValue={editing?.base_price ?? 0}
              />
            </label>
          </div>
          {error && !deleting && (
            <p role="alert" className="inline-error">
              {error}
            </p>
          )}
          {success && (
            <p role="status" className="success-notice">
              {success}
            </p>
          )}
          <div className="form-actions">
            <Button disabled={busy} type="submit">
              {editing ? <Pencil /> : <Plus />}
              {busy ? "Saving…" : editing ? "Save changes" : "Add service"}
            </Button>
            {editing && (
              <Button disabled={busy} variant="outline" type="button" onClick={cancelEdit}>
                Cancel edit
              </Button>
            )}
          </div>
        </form>
      </section>
      <Dialog
        open={!!deleting}
        onOpenChange={(open) => {
          if (!open && !busy) setDeleting(null);
        }}
      >
        <DialogContent>
          <DialogTitle>Delete this service?</DialogTitle>
          <DialogDescription>
            “{deleting?.title}” will be removed from your catalog. This can’t be undone.
          </DialogDescription>
          {error && (
            <p role="alert" className="inline-error">
              {error}
            </p>
          )}
          <div className="form-actions">
            <Button variant="destructive" disabled={busy} onClick={remove}>
              {busy ? "Deleting…" : "Delete service"}
            </Button>
            <Button variant="outline" disabled={busy} onClick={() => setDeleting(null)}>
              Keep service
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
