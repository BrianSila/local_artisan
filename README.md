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
| `/api/artisan`     | Artisan onboarding, profile/image, and catalog management                      |
| `/api/marketplace` | Categories, listing search/details, authenticated WhatsApp contact links       |
| `/api/bookings`    | Booking creation, history, and status workflow                                 |
| `/api/operations`  | Mock M-Pesa checkout, reviews, and disputes                                    |
| `/api/admin`       | Dashboard statistics, artisan verification, suspension, and dispute resolution |

Authenticated requests use `Authorization: Bearer <access_token>`. Registration can create customer or artisan accounts; create the initial administrator with `db-seed-admin`.

## Seed Data

`flask db-seed-all` seeds counties, one representative subcounty per county, and service categories. `flask db-seed-subcounties` can seed the subcounties separately when counties already exist. The bundled subcounty records are a practical starting set, not an exhaustive official boundary dataset; confirm names and boundaries against authoritative data before production use.

## Postman

Import [`Local Artisan API.postman_collection.json`](server/postman/Local%20Artisan%20API.postman_collection.json) and [`Local Artisan API.postman_environment.json`](server/postman/Local%20Artisan%20API.postman_environment.json). Setup requirements, request order, environment values, and destructive cleanup steps are documented in [`server/postman/README.md`](server/postman/README.md).

## Uploads and Deployment

Artisan profile images are saved under `server/app/static/uploads/artisans/` and served as public static files. Configure durable shared object storage for multi-instance production deployments. `flask run` is a development server; deploy with a production WSGI server and configure secrets, PostgreSQL, Redis, and storage separately for each environment.
