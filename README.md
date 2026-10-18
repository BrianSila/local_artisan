# Local Artisan API

Flask REST API for a local-services marketplace. Customers can find artisans, request bookings, and contact verified artisans; artisans manage profiles and service listings; administrators verify artisans and resolve disputes.

## Requirements

- Python 3.11 or newer
- PostgreSQL
- Redis for staging/production cache configuration

## Local Setup

From the repository root:

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create the PostgreSQL database, then configure `server/.env` (do not commit this file):

```dotenv
SECRET_KEY=replace-with-a-long-random-secret
JWT_SECRET_KEY=replace-with-a-different-long-random-secret
DATABASE_URL=postgresql+psycopg://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/artisan_db
```

For example, generate secret values with `python -c 'import secrets; print(secrets.token_urlsafe(48))'`. Run it separately for each key. `DATABASE_URL` must point to an existing database and URL-encode special characters in its username or password.

Apply migrations, seed locations/categories, and create an administrator:

```bash
python -m flask db upgrade
python -m flask db-seed-all
python -m flask db-seed-admin
```

The admin seed command prompts for credentials when `ADMIN_EMAIL`, `ADMIN_NAME`, or `ADMIN_PASSWORD` are not set. Set those variables in `server/.env` to seed non-interactively. Never use development/test passwords outside a private local environment.

Start the development server from `server/`:

```bash
python -m flask --app wsgi:app run --debug
```

The API listens at `http://127.0.0.1:5000`. Health checks are at `/` and `/health`.

## API Areas

| Prefix             | Purpose                                                                        |
| ------------------ | ------------------------------------------------------------------------------ |
| `/api/auth`        | Registration, login, account/profile management, user administration           |
| `/api/locations`   | Counties and subcounties                                                       |
| `/api/artisan`     | Artisan onboarding, profile/images, and catalog management                     |
| `/api/marketplace` | Search, public artisan profiles/reviews, saved artisans, and contact links     |
| `/api/bookings`    | Availability slot management, booking history, and status workflow             |
| `/api/operations`  | Mock M-Pesa checkout, reviews, and disputes                                    |
| `/api/admin`       | Dashboard statistics, artisan verification, suspension, and dispute resolution |

Authenticated requests use `Authorization: Bearer <access_token>`. Registration can create customer or artisan accounts; create the initial administrator with `db-seed-admin`.

## Artisan Nearby Search and Management

Artisan onboarding accepts optional `latitude` and `longitude` values. Existing artisans can set or update both together with `PUT /api/artisan/profile`; coordinates must be decimal degrees (`latitude` -90 to 90, `longitude` -180 to 180). Search using the customer's map/device location with `GET /api/marketplace/search?latitude=-1.286389&longitude=36.817223&radius_km=10`. Nearby results are limited to that radius, ordered closest first, and include `distance_km`. County and subcounty filters remain available and can be combined with a radius search. The maximum radius is 500 km.

The artisan dashboard can load its persisted catalog with authenticated `GET /api/artisan/services`; `POST` and `DELETE` on that route manage entries, and `PUT /api/artisan/services/{service_id}` updates a service owned by the authenticated artisan. The update body uses `category_id`, `title`, `description`, `price_type`, and `base_price`. Admin approval screens can load `GET /api/admin/artisans/pending` and render a Verify action for each item using its `id`: `PATCH /api/admin/artisans/{id}/verify` with `{"is_verified": true}`. Both admin endpoints require an admin access token.

## Artisan Profiles, Availability, and Bookings

Marketplace search and listing-detail responses include artisan name, profile image URL, specialty, verification state, county/subcounty names, average rating, review count, and completed-job count. An artisan with no reviews has `average_rating: null` and `review_count: 0`.

- `GET /api/marketplace/artisans/{artisan_id}` returns the public profile, service catalog, work-photo URLs, and server-calculated trust statistics. Only verified artisans are public.
- `GET /api/marketplace/artisans/{artisan_id}/reviews?page=1&limit=20` returns paginated reviews.
- Authenticated artisans can add work photos with multipart `POST /api/artisan/profile/work-photos` using one or more `work_photos` fields and remove a photo with `DELETE /api/artisan/profile/work-photos/{filename}`. A profile supports up to 10 gallery photos.
- Authenticated artisans can retrieve their prefilled editable profile using `GET /api/artisan/profile`.
- Artisans create, list, and delete one-off availability slots with `POST`, `GET`, and `DELETE /api/bookings/availability`. Create JSON uses ISO-8601 `starts_at` and `ends_at`; slots must be future, positive-duration, and non-overlapping.
- Customers can view open slots using `GET /api/marketplace/artisans/{artisan_id}/availability` and save/remove verified artisans through authenticated `POST /api/marketplace/saved-artisans` (`{"artisan_id": "..."}`), `GET /api/marketplace/saved-artisans`, and `DELETE /api/marketplace/saved-artisans/{artisan_id}`.
- Booking creation now requires `artisan_id`, `service_id`, and `availability_slot_id`; the selected slot must be open and belong to that artisan, and the service must belong to the same artisan. Cancelling a booking releases its slot.
- Booking history includes service and participant display details plus actor-specific `allowed_actions`. Artisan status transitions are pending → accepted → dispatched → completed, with cancellation supported while pending or accepted; customers may cancel their own pending bookings.

## Seed Data

`flask db-seed-all` seeds counties, one representative subcounty per county, and service categories. `flask db-seed-subcounties` can seed the subcounties separately when counties already exist. The bundled subcounty records are a practical starting set, not an exhaustive official boundary dataset; confirm names and boundaries against authoritative data before production use.

## Postman

Import [`Local Artisan API.postman_collection.json`](server/postman/Local%20Artisan%20API.postman_collection.json) and [`Local Artisan API.postman_environment.json`](server/postman/Local%20Artisan%20API.postman_environment.json). Setup requirements, request order, environment values, and destructive cleanup steps are documented in [`server/postman/README.md`](server/postman/README.md).

## Uploads and Deployment

Artisan profile images are saved under `server/app/static/uploads/artisans/` and served as public static files. Configure durable shared object storage for multi-instance production deployments. `flask run` is a development server; deploy with a production WSGI server and configure secrets, PostgreSQL, Redis, and storage separately for each environment.
