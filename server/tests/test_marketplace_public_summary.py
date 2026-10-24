import unittest
from io import BytesIO
from datetime import datetime, timedelta
from tempfile import TemporaryDirectory
from uuid import UUID

from PIL import Image
from app import create_app
from app.accounts.models import ArtisanProfile, User
from app.bookings.models import Booking
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.locations.models import County, SubCounty
from app.operations.models import Review
from app.services.models import ArtisanService, Category


class MarketplacePublicSummaryTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {},
            "JWT_SECRET_KEY": "test-secret",
            "SECRET_KEY": "test-secret",
            "CACHE_TYPE": "NullCache",
        })
        self.upload_dir = TemporaryDirectory(dir=self.app.static_folder)
        self.app.config["UPLOAD_FOLDER"] = self.upload_dir.name
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

        county = County(name="Nairobi", code=47)
        sub_county = SubCounty(name="Westlands", county=county)
        user = User(name="Amina Artisan", email="amina@example.test", password_hash="hash", role="artisan")
        customer = User(name="Customer", email="customer@example.test", password_hash="hash")
        profile = ArtisanProfile(
            user=user,
            bio="Experienced electrical repairs and installation services.",
            experience_years=8,
            primary_phone="254700000001",
            profile_image="uploads/artisans/amina.jpg",
            work_photos=["uploads/artisans/work-1.jpg"],
            is_verified=True,
            county=county,
            sub_county=sub_county,
            specific_address="Westlands",
        )
        category = Category(name="Electrician", slug="electrician", icon_name="Wrench")
        service = ArtisanService(
            artisan_profile=profile,
            category=category,
            title="Home wiring repair",
            description="Diagnosis and repair for home electrical wiring.",
            price_type="fixed",
            base_price=2500,
        )
        db.session.add_all([county, user, customer, category, service])
        db.session.commit()
        self.service_id = str(service.id)
        self.artisan_id = profile.id
        self.artisan_user_id = user.id
        self.customer_user_id = customer.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()
        self.upload_dir.cleanup()

    def test_search_returns_service_and_artisan_summary(self):
        response = self.client.get("/api/marketplace/search")

        self.assertEqual(response.status_code, 200)
        result = response.get_json()["items"][0]
        self.assertEqual(result["artisan_name"], "Amina Artisan")
        self.assertTrue(result["artisan_photo_url"].endswith("/static/uploads/artisans/amina.jpg"))
        self.assertTrue(result["is_verified"])
        self.assertEqual(result["specialty"], "Electrician")
        self.assertEqual(result["county_name"], "Nairobi")
        self.assertEqual(result["sub_county_name"], "Westlands")
        self.assertIsNone(result["average_rating"])
        self.assertEqual(result["review_count"], 0)
        self.assertEqual(result["completed_job_count"], 0)

    def test_listing_detail_returns_same_artisan_summary(self):
        response = self.client.get(f"/api/marketplace/listings/{self.service_id}")

        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result["artisan_name"], "Amina Artisan")
        self.assertEqual(result["specialty"], "Electrician")
        self.assertTrue(result["is_verified"])

    def test_public_artisan_profile_returns_catalog_and_work_photos(self):
        response = self.client.get(f"/api/marketplace/artisans/{self.artisan_id}")

        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result["name"], "Amina Artisan")
        self.assertEqual(result["bio"], "Experienced electrical repairs and installation services.")
        self.assertEqual(result["experience_years"], 8)
        self.assertEqual(result["county_name"], "Nairobi")
        self.assertEqual(result["sub_county_name"], "Westlands")
        self.assertEqual(len(result["services"]), 1)
        self.assertEqual(result["services"][0]["title"], "Home wiring repair")
        self.assertTrue(result["work_photos"][0].endswith("/static/uploads/artisans/work-1.jpg"))

    def test_artisan_can_load_own_profile_for_editing(self):
        response = self.client.get(
            "/api/artisan/profile",
            headers=self._auth_headers(self.artisan_user_id, "artisan"),
        )

        self.assertEqual(response.status_code, 200)
        profile = response.get_json()["profile"]
        self.assertEqual(profile["name"], "Amina Artisan")
        self.assertEqual(profile["bio"], "Experienced electrical repairs and installation services.")
        self.assertEqual(profile["experience_years"], 8)
        self.assertEqual(profile["county_name"], "Nairobi")
        self.assertEqual(profile["sub_county_name"], "Westlands")
        self.assertTrue(profile["profile_image_url"].endswith("/static/uploads/artisans/amina.jpg"))
        self.assertEqual(len(profile["work_photos"]), 1)

        anonymous_response = self.client.get("/api/artisan/profile")
        self.assertEqual(anonymous_response.status_code, 401)

        customer_response = self.client.get(
            "/api/artisan/profile",
            headers=self._auth_headers(self.customer_user_id, "customer"),
        )
        self.assertEqual(customer_response.status_code, 403)

    def test_artisan_can_add_and_remove_work_photos(self):
        image_data = BytesIO()
        Image.new("RGB", (2, 2), color="red").save(image_data, format="PNG")
        image_data.seek(0)
        headers = self._auth_headers(self.artisan_user_id, "artisan")

        upload_response = self.client.post(
            "/api/artisan/profile/work-photos",
            data={"work_photos": [(image_data, "portfolio.png")]},
            headers=headers,
        )
        self.assertEqual(upload_response.status_code, 201)
        photos = upload_response.get_json()["work_photos"]
        self.assertEqual(len(photos), 2)
        filename = photos[-1].rsplit("/", 1)[-1]

        delete_response = self.client.delete(
            f"/api/artisan/profile/work-photos/{filename}",
            headers=headers,
        )
        self.assertEqual(delete_response.status_code, 200)
        profile_response = self.client.get("/api/artisan/profile", headers=headers)
        self.assertEqual(len(profile_response.get_json()["profile"]["work_photos"]), 1)

    def test_artisan_can_update_only_their_own_service(self):
        headers = self._auth_headers(self.artisan_user_id, "artisan")
        response = self.client.put(
            f"/api/artisan/services/{self.service_id}",
            json={
                "category_id": 1,
                "title": "Updated wiring repair",
                "description": "Updated diagnosis and repair for household wiring.",
                "price_type": "hourly",
                "base_price": 3200,
            },
            headers=headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["service"]["title"], "Updated wiring repair")
        self.assertEqual(response.get_json()["service"]["price_type"], "hourly")

        listing_response = self.client.get(f"/api/marketplace/listings/{self.service_id}")
        self.assertEqual(listing_response.get_json()["title"], "Updated wiring repair")
        self.assertEqual(listing_response.get_json()["base_price"], 3200)

        other_user = User(
            name="Another Artisan",
            email="another-artisan@example.test",
            password_hash="hash",
            role="artisan",
        )
        other_profile = ArtisanProfile(
            user=other_user,
            bio="A different artisan with a separate catalog.",
            experience_years=4,
            primary_phone="254700000002",
            county=County.query.first(),
            sub_county=SubCounty.query.first(),
            specific_address="Kilimani",
        )
        db.session.add(other_user)
        db.session.commit()
        unauthorized = self.client.put(
            f"/api/artisan/services/{self.service_id}",
            json={
                "category_id": 1,
                "title": "Attempted unauthorized edit",
                "description": "This update must not change another artisan's service.",
                "price_type": "fixed",
                "base_price": 100,
            },
            headers=self._auth_headers(other_user.id, "artisan"),
        )
        self.assertEqual(unauthorized.status_code, 404)

    def test_public_artisan_profile_hides_unverified_artisans(self):
        profile = db.session.get(ArtisanProfile, self.artisan_id)
        profile.is_verified = False
        db.session.commit()

        response = self.client.get(f"/api/marketplace/artisans/{self.artisan_id}")

        self.assertEqual(response.status_code, 404)

    def test_customer_can_save_list_and_remove_artisan(self):
        customer_headers = self._auth_headers(self.customer_user_id, "customer")
        save_response = self.client.post(
            "/api/marketplace/saved-artisans",
            json={"artisan_id": str(self.artisan_id)},
            headers=customer_headers,
        )
        self.assertEqual(save_response.status_code, 201)
        self.assertTrue(save_response.get_json()["saved"])

        duplicate_response = self.client.post(
            "/api/marketplace/saved-artisans",
            json={"artisan_id": str(self.artisan_id)},
            headers=customer_headers,
        )
        self.assertEqual(duplicate_response.status_code, 200)

        list_response = self.client.get(
            "/api/marketplace/saved-artisans", headers=customer_headers
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.get_json()), 1)
        self.assertEqual(list_response.get_json()[0]["artisan"]["id"], str(self.artisan_id))

        artisan_response = self.client.get(
            "/api/marketplace/saved-artisans",
            headers=self._auth_headers(self.artisan_user_id, "artisan"),
        )
        self.assertEqual(artisan_response.status_code, 403)

        delete_response = self.client.delete(
            f"/api/marketplace/saved-artisans/{self.artisan_id}",
            headers=customer_headers,
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(delete_response.get_json()["saved"])
        self.assertEqual(
            self.client.get("/api/marketplace/saved-artisans", headers=customer_headers).get_json(),
            [],
        )

    def test_booking_history_has_display_details_and_valid_actions(self):
        booking = Booking(
            customer_id=self.customer_user_id,
            artisan_id=self.artisan_id,
            service_id=UUID(self.service_id),
            scheduled_date=datetime.utcnow() + timedelta(days=2),
            status="pending",
            notes="Please call before arriving.",
        )
        db.session.add(booking)
        db.session.commit()
        booking_id = str(booking.id)
        customer_headers = self._auth_headers(self.customer_user_id, "customer")
        artisan_headers = self._auth_headers(self.artisan_user_id, "artisan")

        history = self.client.get("/api/bookings/history", headers=customer_headers)
        self.assertEqual(history.status_code, 200)
        item = history.get_json()["items"][0]
        self.assertEqual(item["service_title"], "Home wiring repair")
        self.assertEqual(item["artisan_name"], "Amina Artisan")
        self.assertEqual(item["customer_name"], "Customer")
        self.assertEqual(item["allowed_actions"], ["cancelled"])

        artisan_history = self.client.get("/api/bookings/history", headers=artisan_headers)
        self.assertEqual(
            artisan_history.get_json()["items"][0]["allowed_actions"],
            ["accepted", "cancelled"],
        )

        forbidden_transition = self.client.patch(
            f"/api/bookings/{booking_id}/status",
            json={"status": "completed"},
            headers=artisan_headers,
        )
        self.assertEqual(forbidden_transition.status_code, 403)

        for status in ["accepted", "dispatched", "completed"]:
            response = self.client.patch(
                f"/api/bookings/{booking_id}/status",
                json={"status": status},
                headers=artisan_headers,
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["booking"]["status"], status)

        terminal_transition = self.client.patch(
            f"/api/bookings/{booking_id}/status",
            json={"status": "cancelled"},
            headers=artisan_headers,
        )
        self.assertEqual(terminal_transition.status_code, 403)

    def test_review_aggregates_and_public_reviews_are_paginated(self):
        profile = db.session.get(ArtisanProfile, self.artisan_id)
        customer_id = self.customer_user_id
        bookings = [
            Booking(
                customer_id=customer_id,
                artisan_id=self.artisan_id,
                service_id=UUID(self.service_id),
                scheduled_date=datetime.utcnow() - timedelta(days=index + 1),
                status="completed",
            )
            for index in range(2)
        ]
        bookings.append(
            Booking(
                customer_id=customer_id,
                artisan_id=self.artisan_id,
                service_id=UUID(self.service_id),
                scheduled_date=datetime.utcnow() + timedelta(days=1),
                status="pending",
            )
        )
        db.session.add_all(bookings)
        db.session.flush()
        db.session.add_all([
            Review(booking_id=bookings[0].id, artisan_id=profile.id, rating=4, comment="Good work"),
            Review(booking_id=bookings[1].id, artisan_id=profile.id, rating=5, comment="Excellent"),
        ])
        db.session.commit()

        listing_response = self.client.get("/api/marketplace/search")
        listing = listing_response.get_json()["items"][0]
        self.assertEqual(listing["average_rating"], 4.5)
        self.assertEqual(listing["review_count"], 2)
        self.assertEqual(listing["completed_job_count"], 2)

        profile_response = self.client.get(f"/api/marketplace/artisans/{self.artisan_id}")
        profile_data = profile_response.get_json()
        self.assertEqual(profile_data["average_rating"], 4.5)
        self.assertEqual(profile_data["review_count"], 2)

        reviews_response = self.client.get(
            f"/api/marketplace/artisans/{self.artisan_id}/reviews?page=1&limit=1"
        )
        reviews_data = reviews_response.get_json()
        self.assertEqual(reviews_data["total"], 2)
        self.assertEqual(reviews_data["page"], 1)
        self.assertEqual(len(reviews_data["items"]), 1)

    def test_availability_slots_gate_bookings_and_release_on_cancel(self):
        starts_at = (datetime.utcnow() + timedelta(days=2)).replace(microsecond=0)
        ends_at = starts_at + timedelta(hours=1)
        artisan_headers = self._auth_headers(self.artisan_user_id, "artisan")
        customer_headers = self._auth_headers(self.customer_user_id, "customer")

        create_response = self.client.post(
            "/api/bookings/availability",
            json={"starts_at": starts_at.isoformat(), "ends_at": ends_at.isoformat()},
            headers=artisan_headers,
        )
        self.assertEqual(create_response.status_code, 201)
        slot_id = create_response.get_json()["slot"]["id"]

        public_response = self.client.get(
            f"/api/marketplace/artisans/{self.artisan_id}/availability"
        )
        self.assertEqual(public_response.status_code, 200)
        self.assertEqual([slot["id"] for slot in public_response.get_json()], [slot_id])

        booking_data = {
            "artisan_id": str(self.artisan_id),
            "service_id": self.service_id,
            "availability_slot_id": slot_id,
            "notes": "Please call before arriving.",
        }
        booking_response = self.client.post(
            "/api/bookings", json=booking_data, headers=customer_headers
        )
        self.assertEqual(booking_response.status_code, 201)
        booking_id = booking_response.get_json()["booking"]["id"]

        duplicate_response = self.client.post(
            "/api/bookings", json=booking_data, headers=customer_headers
        )
        self.assertEqual(duplicate_response.status_code, 400)

        unavailable_response = self.client.get(
            f"/api/marketplace/artisans/{self.artisan_id}/availability"
        )
        self.assertEqual(unavailable_response.get_json(), [])

        cancel_response = self.client.patch(
            f"/api/bookings/{booking_id}/status",
            json={"status": "cancelled"},
            headers=customer_headers,
        )
        self.assertEqual(cancel_response.status_code, 200)

        released_response = self.client.get(
            f"/api/marketplace/artisans/{self.artisan_id}/availability"
        )
        self.assertEqual([slot["id"] for slot in released_response.get_json()], [slot_id])

    def test_overlapping_availability_slots_are_rejected(self):
        starts_at = (datetime.utcnow() + timedelta(days=3)).replace(microsecond=0)
        headers = self._auth_headers(self.artisan_user_id, "artisan")
        first_response = self.client.post(
            "/api/bookings/availability",
            json={
                "starts_at": starts_at.isoformat(),
                "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
            },
            headers=headers,
        )
        self.assertEqual(first_response.status_code, 201)

        overlap_response = self.client.post(
            "/api/bookings/availability",
            json={
                "starts_at": (starts_at + timedelta(minutes=30)).isoformat(),
                "ends_at": (starts_at + timedelta(hours=2)).isoformat(),
            },
            headers=headers,
        )
        self.assertEqual(overlap_response.status_code, 400)

    def _auth_headers(self, user_id, role):
        token = create_access_token(
            identity=str(user_id), additional_claims={"role": role}
        )
        return {"Authorization": f"Bearer {token}"}


if __name__ == "__main__":
    unittest.main()
