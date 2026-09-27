# Postman API Tests

## Import and Configure

1. Start the API from `server` with `flask run`.
2. Import `Local Artisan API.postman_collection.json` and `Local Artisan API.postman_environment.json` into Postman, then select the local environment.
3. Set `adminEmail` and `adminPassword` to an existing administrator account. Public registration only accepts `customer` or `artisan` roles, so it cannot create an admin.
4. Ensure the database has at least one county with a subcounty and at least one service category. The counties request selects the first county/subcounty pair it finds; if it finds none, set `countyId`, `subCountyId`, and `categoryId` to valid database IDs in the environment. `db-seed-all` seeds counties, but this project currently needs subcounties and categories available separately.
5. Confirm the latest Alembic migrations are applied. The artisan image upload request requires choosing an image file in Postman when prompted. A PNG, JPEG, GIF, or WebP under 5 MB is accepted.

## Run

Run the collection in its displayed order. It registers fresh customer, artisan, and disposable accounts; captures their IDs/tokens; onboards and verifies the artisan; creates a catalog service; then exercises marketplace, booking, payment mock, review, dispute, and admin resolution flows. The final **Cleanup** folder deletes the test service, changes the test customer password, and deactivates that customer. Those actions are intentional; use test data and recreate/select fresh accounts on another run.

The collection-level test asserts every response is 2xx. Request tests save values such as `customerToken`, `artisanProfileId`, `serviceId`, `bookingId`, and `disputeId` into the selected environment for later requests.

## Request Bodies

JSON bodies for registration, profile updates, service creation, booking creation/status changes, M-Pesa checkout, review, dispute, role/suspension updates, password change, and dispute resolution are included in the collection. Artisan onboarding uses multipart fields (`bio`, `experience_years`, `primary_phone`, `county_id`, `sub_county_id`, `specific_address`). Profile-image replacement uses multipart `profile_image` and the Postman file picker.

The collection covers all current registered application routes: root/health, locations, accounts, artisan, marketplace, bookings, operations, admin, and the static profile-image URL. It does not call Flask's generic static route with arbitrary paths.
