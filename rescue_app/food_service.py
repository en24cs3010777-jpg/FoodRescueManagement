"""
Food Rescue Operations and Business Logic Module for MongoDB.
Handles listing, filtering, claiming, collecting, and tracking surplus food items.
"""

from datetime import datetime, timezone
import re
from rescue_app.db import (
    get_food_collection,
    get_claims_collection,
    to_object_id,
    serialize_doc
)


FOOD_CATEGORIES = [
    "Cooked Meals",
    "Bakery & Bread",
    "Fresh Produce (Fruits & Vegetables)",
    "Packaged Food",
    "Groceries & Grains",
    "Dairy Products",
    "Beverages",
    "Other"
]

FOOD_TYPES = [
    "Vegetarian",
    "Non-Vegetarian",
    "Vegan"
]


def add_food_item(provider_user, title, description, category, food_type, quantity,
                  pickup_address, pickup_city, pickup_time_slot, expiry_info,
                  contact_person=None, contact_phone=None):
    """
    Creates a new food surplus donation listing.
    """
    title = title.strip()
    if not title:
        return None, "Food title is required."
    if not quantity:
        return None, "Quantity or number of servings is required."
    if not pickup_address:
        return None, "Pickup address is required."

    food_coll = get_food_collection()
    now = datetime.now(timezone.utc)

    provider_id = str(provider_user.get('id') or provider_user.get('_id'))
    provider_name = provider_user.get('full_name') or provider_user.get('username')
    phone = contact_phone or provider_user.get('phone', '')
    person = contact_person or provider_name

    food_doc = {
        "provider_id": provider_id,
        "provider_username": provider_user.get('username'),
        "provider_name": provider_name,
        "provider_phone": phone,
        "contact_person": person,
        "contact_phone": phone,
        "title": title,
        "description": description.strip(),
        "category": category if category in FOOD_CATEGORIES else "Other",
        "food_type": food_type if food_type in FOOD_TYPES else "Vegetarian",
        "quantity": quantity.strip(),
        "pickup_address": pickup_address.strip(),
        "pickup_city": pickup_city.strip() if pickup_city else "",
        "pickup_time_slot": pickup_time_slot.strip() if pickup_time_slot else "Flexible / Contact Provider",
        "expiry_info": expiry_info.strip() if expiry_info else "Best consumed today",
        "status": "available",  # 'available', 'claimed', 'collected', 'cancelled'
        "claimed_by_id": None,
        "claimed_by_username": None,
        "claimed_by_name": None,
        "claimed_by_phone": None,
        "claimed_at": None,
        "claim_notes": None,
        "collected_at": None,
        "created_at": now,
        "updated_at": now,
    }

    result = food_coll.insert_one(food_doc)
    food_doc['_id'] = result.inserted_id
    return serialize_doc(food_doc), None


def get_available_food_items(search_query=None, category=None, food_type=None, city=None):
    """
    Fetches all currently available food listings with optional search and filters.
    """
    food_coll = get_food_collection()
    query = {"status": "available"}

    if search_query:
        regex = re.compile(re.escape(search_query.strip()), re.IGNORECASE)
        query["$or"] = [
            {"title": regex},
            {"description": regex},
            {"pickup_city": regex},
            {"pickup_address": regex}
        ]

    if category and category != "All":
        query["category"] = category

    if food_type and food_type != "All":
        query["food_type"] = food_type

    if city and city.strip():
        query["pickup_city"] = re.compile(re.escape(city.strip()), re.IGNORECASE)

    cursor = food_coll.find(query).sort("created_at", -1)
    return [serialize_doc(doc) for doc in cursor]


def get_food_item_by_id(food_id):
    """Retrieves a single food listing by ID."""
    oid = to_object_id(food_id)
    if not oid:
        return None
    food_coll = get_food_collection()
    doc = food_coll.find_one({"_id": oid})
    return serialize_doc(doc)


def claim_food_item(food_id, seeker_user, claim_notes=""):
    """
    Atomically claims an available food item for a seeker.
    Uses atomic find_one_and_update to prevent race conditions.
    """
    oid = to_object_id(food_id)
    if not oid:
        return False, "Invalid food listing ID."

    food_coll = get_food_collection()
    seeker_id = str(seeker_user.get('id') or seeker_user.get('_id'))

    # Verify user isn't claiming their own food
    existing = food_coll.find_one({"_id": oid})
    if not existing:
        return False, "Food listing not found."

    if existing.get('provider_id') == seeker_id:
        return False, "You cannot claim food that you listed yourself!"

    now = datetime.now(timezone.utc)
    updated_doc = food_coll.find_one_and_update(
        {"_id": oid, "status": "available"},
        {
            "$set": {
                "status": "claimed",
                "claimed_by_id": seeker_id,
                "claimed_by_username": seeker_user.get('username'),
                "claimed_by_name": seeker_user.get('full_name') or seeker_user.get('username'),
                "claimed_by_phone": seeker_user.get('phone', ''),
                "claimed_at": now,
                "claim_notes": claim_notes.strip(),
                "updated_at": now
            }
        }
    )

    if not updated_doc:
        return False, "This food listing is no longer available (it may have just been claimed)."

    # Log to claims collection for audit/history
    claims_coll = get_claims_collection()
    claims_coll.insert_one({
        "food_id": str(oid),
        "food_title": existing.get('title'),
        "provider_id": existing.get('provider_id'),
        "provider_name": existing.get('provider_name'),
        "seeker_id": seeker_id,
        "seeker_name": seeker_user.get('full_name'),
        "seeker_phone": seeker_user.get('phone'),
        "status": "claimed",
        "notes": claim_notes.strip(),
        "claimed_at": now,
    })

    return True, "Food item successfully claimed! Please coordinate pickup with the provider."


def mark_food_collected(food_id, user_id):
    """
    Marks a claimed food item as successfully collected / picked up.
    Allowed for either the provider or the seeker of the item.
    """
    oid = to_object_id(food_id)
    if not oid:
        return False, "Invalid food listing ID."

    food_coll = get_food_collection()
    item = food_coll.find_one({"_id": oid})
    if not item:
        return False, "Food item not found."

    uid = str(user_id)
    # Check permission: must be provider or seeker
    if item.get('provider_id') != uid and item.get('claimed_by_id') != uid:
        return False, "You do not have permission to update this food item."

    if item.get('status') == 'collected':
        return False, "This item has already been marked as collected."

    now = datetime.now(timezone.utc)
    food_coll.update_one(
        {"_id": oid},
        {"$set": {"status": "collected", "collected_at": now, "updated_at": now}}
    )

    # Update claims collection as well
    claims_coll = get_claims_collection()
    claims_coll.update_many(
        {"food_id": str(oid)},
        {"$set": {"status": "collected", "collected_at": now}}
    )

    return True, "Food marked as collected! Thank you for rescuing food."


def cancel_food_item(food_id, user_id):
    """
    Cancels or deletes a food listing (only allowed by the provider who created it).
    """
    oid = to_object_id(food_id)
    if not oid:
        return False, "Invalid food listing ID."

    food_coll = get_food_collection()
    item = food_coll.find_one({"_id": oid})
    if not item:
        return False, "Food item not found."

    if item.get('provider_id') != str(user_id):
        return False, "Only the provider who created this listing can delete or cancel it."

    if item.get('status') == 'collected':
        return False, "Completed rescues cannot be cancelled."

    now = datetime.now(timezone.utc)
    food_coll.update_one(
        {"_id": oid},
        {"$set": {"status": "cancelled", "updated_at": now}}
    )

    return True, "Food listing cancelled."


def get_provider_listings(provider_id):
    """Returns all food listings created by a specific provider."""
    food_coll = get_food_collection()
    cursor = food_coll.find({"provider_id": str(provider_id)}).sort("created_at", -1)
    return [serialize_doc(doc) for doc in cursor]


def get_seeker_claims(seeker_id):
    """Returns all food listings claimed or collected by a specific seeker."""
    food_coll = get_food_collection()
    cursor = food_coll.find({"claimed_by_id": str(seeker_id)}).sort("claimed_at", -1)
    return [serialize_doc(doc) for doc in cursor]


def get_dashboard_stats(user_id, active_mode='provider'):
    """
    Calculates summary metrics for the user dashboard based on active mode.
    """
    food_coll = get_food_collection()
    uid = str(user_id)

    # Global community stats
    total_rescued_all = food_coll.count_documents({"status": "collected"})
    total_available_all = food_coll.count_documents({"status": "available"})

    if active_mode == 'provider':
        my_total = food_coll.count_documents({"provider_id": uid})
        my_available = food_coll.count_documents({"provider_id": uid, "status": "available"})
        my_claimed = food_coll.count_documents({"provider_id": uid, "status": "claimed"})
        my_collected = food_coll.count_documents({"provider_id": uid, "status": "collected"})

        return {
            "mode": "provider",
            "stat_1_label": "Total Food Listed",
            "stat_1_val": my_total,
            "stat_2_label": "Currently Available",
            "stat_2_val": my_available,
            "stat_3_label": "Pending Pickup",
            "stat_3_val": my_claimed,
            "stat_4_label": "Successfully Rescued",
            "stat_4_val": my_collected,
            "community_rescued": total_rescued_all,
            "community_available": total_available_all
        }
    else:  # seeker mode
        my_claimed = food_coll.count_documents({"claimed_by_id": uid, "status": "claimed"})
        my_collected = food_coll.count_documents({"claimed_by_id": uid, "status": "collected"})
        my_total_claims = food_coll.count_documents({"claimed_by_id": uid})

        return {
            "mode": "seeker",
            "stat_1_label": "Available to Rescue",
            "stat_1_val": total_available_all,
            "stat_2_label": "My Pending Claims",
            "stat_2_val": my_claimed,
            "stat_3_label": "My Completed Pickups",
            "stat_3_val": my_collected,
            "stat_4_label": "Total Claims",
            "stat_4_val": my_total_claims,
            "community_rescued": total_rescued_all,
            "community_available": total_available_all
        }
