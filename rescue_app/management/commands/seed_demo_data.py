"""
Django Management Command: seed_demo_data
Seeds sample Food Providers, Food Seekers, and realistic Food Surplus items into MongoDB.
Usage:
    python manage.py seed_demo_data
"""

from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from rescue_app.db import (
    check_db_connection,
    get_users_collection,
    get_food_collection,
    get_claims_collection,
    init_indexes
)
from rescue_app.auth_helper import create_user
from rescue_app.food_service import add_food_item, claim_food_item, mark_food_collected


class Command(BaseCommand):
    help = "Seeds MongoDB database with realistic demo data for College Project testing."

    def handle(self, *args, **options):
        self.stdout.write("Testing MongoDB connection...")
        connected, err = check_db_connection()
        if not connected:
            self.stderr.write(self.style.ERROR(f"Failed to connect to MongoDB: {err}"))
            self.stderr.write(self.style.WARNING("Make sure MongoDB is running locally or configure MONGO_URI in .env"))
            return

        self.stdout.write(self.style.SUCCESS("MongoDB connected successfully!"))
        init_indexes()

        users_coll = get_users_collection()
        food_coll = get_food_collection()
        claims_coll = get_claims_collection()

        # Clean old demo data if user wants fresh seed
        self.stdout.write("Checking demo accounts...")

        # 1. Create Demo Provider
        provider = users_coll.find_one({"username": "provider_demo"})
        if not provider:
            provider, err = create_user(
                username="provider_demo",
                email="provider@foodrescue.org",
                password="password123",
                full_name="Spice Garden Banquet & Restaurant",
                phone="+91 98765 43210",
                role="provider",
                organization="Spice Garden Hospitality",
                address="Plot 14, Ring Road, Sector 18, City Center"
            )
            self.stdout.write(self.style.SUCCESS("Created demo provider: provider_demo / password123"))
        else:
            from rescue_app.db import serialize_doc
            provider = serialize_doc(provider)
            self.stdout.write("Demo provider already exists.")

        # 2. Create Demo Seeker
        seeker = users_coll.find_one({"username": "seeker_demo"})
        if not seeker:
            seeker, err = create_user(
                username="seeker_demo",
                email="seeker@foodrescue.org",
                password="password123",
                full_name="Hope Shelter & Community NGO",
                phone="+91 91234 56789",
                role="seeker",
                organization="Hope Foundation India",
                address="Community Welfare Building, Block C, West Colony"
            )
            self.stdout.write(self.style.SUCCESS("Created demo seeker: seeker_demo / password123"))
        else:
            from rescue_app.db import serialize_doc
            seeker = serialize_doc(seeker)
            self.stdout.write("Demo seeker already exists.")

        # 3. Create Sample Food Items
        existing_items = food_coll.count_documents({"provider_id": provider['id']})
        if existing_items == 0:
            self.stdout.write("Populating sample food listings...")

            # Item 1: Available Veg Meals
            item1, _ = add_food_item(
                provider_user=provider,
                title="Fresh Veg Biryani & Mint Raita (35 Servings)",
                description="Hygienically prepared during corporate lunch. Packed in food-grade aluminum trays. Kept warm.",
                category="Cooked Meals",
                food_type="Vegetarian",
                quantity="35 servings",
                pickup_address="Spice Garden Banquet Kitchen, Ring Road",
                pickup_city="City Center",
                pickup_time_slot="Today between 4:00 PM - 7:30 PM",
                expiry_info="Best consumed today before 10:00 PM",
                contact_person="Chef Arvind",
                contact_phone="+91 98765 43210"
            )

            # Item 2: Available Bakery
            item2, _ = add_food_item(
                provider_user=provider,
                title="Assorted Artisan Breads & Tea Cakes (20 Boxes)",
                description="Freshly baked whole wheat loaves, buns, and eggless tea cakes from today's batch.",
                category="Bakery & Bread",
                food_type="Vegetarian",
                quantity="20 boxes",
                pickup_address="Spice Garden Bakery Counter, Ring Road",
                pickup_city="City Center",
                pickup_time_slot="Today until 9:00 PM",
                expiry_info="Best before 48 hours",
                contact_person="Arvind",
                contact_phone="+91 98765 43210"
            )

            # Item 3: Available Fresh Produce
            item3, _ = add_food_item(
                provider_user=provider,
                title="Organic Apples, Bananas & Seasonal Greens (15 kg)",
                description="Surplus fresh fruit crates and washed spinach/coriander from hotel supplies.",
                category="Fresh Produce (Fruits & Vegetables)",
                food_type="Vegan",
                quantity="15 kg",
                pickup_address="Back Gate Goods Receiving Area, Spice Garden",
                pickup_city="City Center",
                pickup_time_slot="Tomorrow morning 8:00 AM - 11:00 AM",
                expiry_info="Best before 3 days",
                contact_person="Store Manager",
                contact_phone="+91 98765 43210"
            )

            # Item 4: Claimed Item (Seeker claimed, pending pickup)
            item4, _ = add_food_item(
                provider_user=provider,
                title="Dal Makhani, Jeera Rice & Roti Meal Boxes (25 Plates)",
                description="Surplus evening catering trays. Packed in individual meal boxes with spoons.",
                category="Cooked Meals",
                food_type="Vegetarian",
                quantity="25 plates",
                pickup_address="Plot 14, Sector 18, City Center",
                pickup_city="City Center",
                pickup_time_slot="Today between 6:00 PM - 8:30 PM",
                expiry_info="Best before tonight 11 PM",
                contact_person="Manager Rajat",
                contact_phone="+91 98765 43210"
            )
            if item4:
                claim_food_item(item4['id'], seeker, claim_notes="NGO van arriving around 6:45 PM for community dinner.")

            # Item 5: Collected / Rescued Item
            item5, _ = add_food_item(
                provider_user=provider,
                title="Veg Club Sandwiches & Juice Tetrapacks (30 Units)",
                description="Packaged lunch boxes from conference seminar. Completely untouched.",
                category="Packaged Food",
                food_type="Vegetarian",
                quantity="30 units",
                pickup_address="Plot 14, Sector 18, City Center",
                pickup_city="City Center",
                pickup_time_slot="Completed",
                expiry_info="Consumed",
                contact_person="Chef Arvind",
                contact_phone="+91 98765 43210"
            )
            if item5:
                claim_food_item(item5['id'], seeker, claim_notes="Shelter volunteers picked up on time.")
                mark_food_collected(item5['id'], provider['id'])

            self.stdout.write(self.style.SUCCESS("Sample food listings created successfully!"))
        else:
            self.stdout.write("Food listings already exist.")

        self.stdout.write(self.style.SUCCESS("""
=======================================================
Demo Seed Complete! Test Credentials:
-------------------------------------------------------
1. Food Provider Account:
   Username: provider_demo
   Password: password123

2. Food Seeker Account:
   Username: seeker_demo
   Password: password123
=======================================================
"""))
