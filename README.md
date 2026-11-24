# 🌱 Food Rescue Management System

A web-based platform built with **Django (Python)** and **MongoDB (NoSQL)** designed to bridge the gap between surplus food and individuals/NGOs in need. The system empowers **Food Providers** (restaurants, caterers, banquet halls, households) to list extra edible meals and allows **Food Seekers** (NGOs, shelters, community volunteers) to claim and collect fresh food before it goes to waste.

Developed as a college project featuring pure, professional **HTML5 & CSS3** (no external frontend frameworks), robust **NoSQL document database architecture**, and secure user account management.

---

## 🌟 Key Features

### 1. Unified Authentication (Two User Types)
- **Shared Login & Signup**: Food Providers and Food Seekers register through a unified portal.
- **Two Roles**:
  - 🍲 **Food Provider**: Has surplus food to donate.
  - 🤝 **Food Seeker**: Rescues food for community distribution or personal need.
- **Dashboard Mode Switcher**: Any user can seamlessly specify and toggle between **"Provide Food"** and **"Seek Food"** modes directly on their dashboard with a single click.

### 2. Core Dashboard Capabilities
- **Active Mode Indicator**: Prominently displays whether the user is operating as a Provider or Seeker.
- **Summary Metrics**: Real-time counters for items listed, available food, pending claims, and completed rescues.
- **Quick-Access Action Tiles**:
  - ➕ **Add Food**: Simple form to list surplus food items.
  - 🔍 **View Food**: Search and browse available food listings across categories.
  - 📦 / 🤝 **Collect / Manage Food**: Manage listings (for providers) or track claimed meals (for seekers).
  - ⚙️ **Account Settings**: Full profile and security control.

### 3. Food Listing & Claiming
- **Add Surplus Food**: Title, Category, Veg/Non-Veg/Vegan flag, Quantity/Servings, Pickup Address, City, Pickup Time Window, Expiry/Best Before info, and contact details.
- **Search & Filter**: Keyword search (dish name, description, address), category filter, dietary filter, and city filter.
- **Atomic Concurrency Protection**: Uses MongoDB's atomic `find_one_and_update` operation to ensure no two seekers can claim the same food item simultaneously.
- **Pickup & Collection Verification**: Either the provider or the seeker can mark an item as **Collected / Rescued** once handover is complete.

### 4. Comprehensive Account Settings
- **Update Account**: Update Full Name, Email, Phone Number, Organization/Affiliation, Address, and Default Role.
- **Password Setting**: Secure password update with old-password verification and Django's PBKDF2 SHA-256 cryptographic hashing.
- **Delete Account (Danger Zone)**: Permanently wipes the user from MongoDB and cancels any uncollected food listings upon password confirmation.

### 5. Frontend Design
- **Pure HTML5 & CSS3**: No Bootstrap, Tailwind, React, or third-party CDN libraries.
- **100% Offline Compatible**: Operates reliably without an active internet connection.
- **Professional & Responsive**: Mobile-friendly layout using clean CSS Grid and Flexbox with a modern green/slate palette.

---

## 🏗️ Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.15 + Django 6.1 | Web framework, routing, templating, session handling |
| **Database** | MongoDB (NoSQL) | High-performance document database |
| **DB Driver** | PyMongo 4.19 + dnspython | Official MongoDB Python driver |
| **Frontend** | Pure HTML5 + CSS3 | Semantic markup and custom responsive styling |
| **Security** | PBKDF2 SHA-256 | Cryptographic password hashing |

---

## 🗄️ MongoDB NoSQL Database Schema

### Collection: `users`
```json
{
  "_id": ObjectId("670e3..."),
  "username": "spice_garden",
  "email": "spice@restaurant.com",
  "password": "pbkdf2_sha256$870000$...",
  "full_name": "Spice Garden Banquet",
  "phone": "+91 9876543210",
  "default_role": "provider", // "provider" or "seeker"
  "organization": "Spice Garden Hospitality",
  "address": "Plot 14, Ring Road, Sector 18, City Center",
  "created_at": ISODate("2026-10-15T10:00:00Z"),
  "updated_at": ISODate("2026-10-15T10:00:00Z")
}
```

### Collection: `food_items`
```json
{
  "_id": ObjectId("670e4..."),
  "provider_id": "670e3...",
  "provider_username": "spice_garden",
  "provider_name": "Spice Garden Banquet",
  "provider_phone": "+91 9876543210",
  "contact_person": "Chef Arvind",
  "contact_phone": "+91 9876543210",
  "title": "Fresh Veg Biryani & Mint Raita (35 Servings)",
  "description": "Packed in food-grade aluminum trays. Kept hot.",
  "category": "Cooked Meals",
  "food_type": "Vegetarian", // "Vegetarian", "Non-Vegetarian", "Vegan"
  "quantity": "35 servings",
  "pickup_address": "Spice Garden Banquet Kitchen, Ring Road",
  "pickup_city": "City Center",
  "pickup_time_slot": "Today between 4:00 PM - 7:30 PM",
  "expiry_info": "Best consumed today before 10:00 PM",
  "status": "available", // "available", "claimed", "collected", "cancelled"
  "claimed_by_id": null, // Seeker ObjectId string when claimed
  "claimed_by_name": null,
  "claimed_by_phone": null,
  "claimed_at": null,
  "claim_notes": null,
  "collected_at": null,
  "created_at": ISODate("2026-10-15T11:00:00Z"),
  "updated_at": ISODate("2026-10-15T11:00:00Z")
}
```

### Collection: `claims`
```json
{
  "_id": ObjectId("670e5..."),
  "food_id": "670e4...",
  "food_title": "Fresh Veg Biryani & Mint Raita (35 Servings)",
  "provider_id": "670e3...",
  "seeker_id": "670e2...",
  "seeker_name": "Hope Shelter Foundation",
  "seeker_phone": "+91 9123456789",
  "status": "claimed", // "claimed", "collected"
  "notes": "Van arriving at 5:00 PM",
  "claimed_at": ISODate("2026-10-15T11:30:00Z"),
  "collected_at": null
}
```

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.10+ installed
- MongoDB installed locally **OR** a free [MongoDB Atlas](https://www.mongodb.com/atlas) cloud cluster

### 2. Activate Virtual Environment
```bash
# On macOS / Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database Connection (`.env`)
A `.env` file is included in the project root:
```env
# For Local MongoDB (Default):
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=food_rescue_db

# OR For Cloud MongoDB Atlas (Free Tier):
# MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
```

### 5. Apply Migrations (for Django Sessions)
```bash
python manage.py migrate
```

### 6. Populate Realistic Demo Data (Optional but Recommended)
Run the custom management command to automatically create demo provider and seeker accounts with sample food items:
```bash
python manage.py seed_demo_data
```

**Pre-seeded Demo Accounts:**
| Account Type | Username | Password |
| :--- | :--- | :--- |
| **Food Provider** | `provider_demo` | `password123` |
| **Food Seeker** | `seeker_demo` | `password123` |

### 7. Run Unit Tests
```bash
python manage.py test rescue_app
```

### 8. Start the Web Server
```bash
python manage.py runserver
```
Open your browser and navigate to: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔍 Database Diagnostics Page
You can verify your MongoDB connection and see active collections at any time by navigating to:
**[http://127.0.0.1:8000/db-status/](http://127.0.0.1:8000/db-status/)**

---

## 🎓 College Viva / Presentation Q&A

**Q1: Why choose MongoDB (NoSQL) over a Relational SQL Database for this project?**
> Food rescue listings have dynamic, semi-structured attributes (varying expiry windows, specific dietary notes, differing quantity units like servings vs kg vs boxes, packaging instructions). MongoDB's schema flexibility avoids costly table alter migrations. Furthermore, MongoDB document structures allow atomic state transitions (like claiming a meal) in a single document update.

**Q2: How does the application avoid race conditions when two seekers claim the same meal?**
> The system uses PyMongo's atomic `find_one_and_update({"_id": food_id, "status": "available"}, {"$set": {"status": "claimed", ...}})` method. The operation succeeds for only the first request; the second request receives `None` and is safely notified that the item has already been claimed.

**Q3: How are passwords stored securely?**
> Passwords are never stored in plaintext. They are hashed using Django's standard PBKDF2 algorithm with a SHA-256 hash and a unique salt per user before insertion into MongoDB.
