import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6] # blank

    # Theme colors
    PRIMARY_DARK = RGBColor(20, 83, 45)      # #14532d (Dark Forest Green)
    PRIMARY_GREEN = RGBColor(22, 163, 74)    # #16a34a (Emerald Green)
    PRIMARY_LIGHT = RGBColor(220, 252, 231)  # #dcfce7
    TEXT_DARK = RGBColor(15, 23, 42)         # #0f172a (Navy Slate)
    TEXT_MUTED = RGBColor(100, 116, 139)     # #64748b
    BG_LIGHT = RGBColor(248, 250, 252)       # #f8fafc
    WHITE = RGBColor(255, 255, 255)
    BORDER_COLOR = RGBColor(226, 232, 240)
    AMBER = RGBColor(217, 119, 6)

    def add_header(slide, title_text, category_text="FOOD RESCUE MANAGEMENT SYSTEM"):
        # Top banner shape
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        banner.fill.solid()
        banner.fill.fore_color.rgb = PRIMARY_DARK
        banner.line.color.rgb = PRIMARY_DARK

        # Category text
        txBox1 = slide.shapes.add_textbox(Inches(0.8), Inches(0.15), Inches(11.7), Inches(0.3))
        tf1 = txBox1.text_frame
        tf1.word_wrap = True
        p1 = tf1.paragraphs[0]
        p1.text = category_text.upper()
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = PRIMARY_LIGHT

        # Title text
        txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(11.7), Inches(0.6))
        tf2 = txBox2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = WHITE

        # Footer
        footer_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.02))
        footer_line.fill.solid()
        footer_line.fill.fore_color.rgb = BORDER_COLOR
        footer_line.line.color.rgb = BORDER_COLOR

        tx_foot = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.3))
        tff = tx_foot.text_frame
        pf = tff.paragraphs[0]
        pf.text = "Food Rescue Management System • College Project • Django & MongoDB NoSQL Architecture"
        pf.font.size = Pt(9)
        pf.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = PRIMARY_DARK
    bg1.line.color.rgb = PRIMARY_DARK

    # Card container in center
    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.0), Inches(10.933), Inches(5.5))
    card1.fill.solid()
    card1.fill.fore_color.rgb = WHITE
    card1.line.color.rgb = BORDER_COLOR

    tbox = s1.shapes.add_textbox(Inches(1.8), Inches(1.5), Inches(9.7), Inches(4.5))
    tf = tbox.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🌱 ZERO HUNGER INITIATIVE • COLLEGE PROJECT"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN

    p = tf.add_paragraph()
    p.text = "Food Rescue Management System"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = TEXT_DARK
    p.space_after = Pt(12)

    p = tf.add_paragraph()
    p.text = "A decentralized web application connecting food providers with food seekers to eliminate food waste."
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(24)

    p = tf.add_paragraph()
    p.text = "Key Technical Highlights:"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = TEXT_DARK

    highlights = [
        "Backend: Django 6.1 (Python 3.15) with structured modular architecture",
        "Database: MongoDB NoSQL Atlas Cloud with Atomic Concurrency Control (find_one_and_update)",
        "Frontend: Pure Semantic HTML5 & CSS3 (Zero external UI dependencies, 100% offline-ready)",
        "User Roles: Food Provider & Food Seeker with unified auth & 1-click dashboard mode switcher"
    ]
    for h in highlights:
        p = tf.add_paragraph()
        p.text = f"✔  {h}"
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 2: PROJECT OVERVIEW & PROBLEM STATEMENT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Project Overview & Problem Statement", "PROJECT BACKGROUND")

    # 3 Column Cards
    col_width = Inches(3.64)
    col_gap = Inches(0.4)
    left_margin = Inches(0.8)
    top_pos = Inches(1.6)

    cards_data = [
        ("The Challenge", "Millions of tons of perfectly edible food from restaurants, banquet halls, weddings, and supermarkets are discarded daily while communities face food insecurity.\n\nTraditional donation methods lack real-time coordination, leading to delays and spoilage of perishable cooked meals.", TEXT_DARK, AMBER),
        ("The Solution", "A streamlined web platform connecting Food Providers and Food Seekers.\n\n• Real-Time Surplus Listings\n• Transparent Pickup Time Slots\n• 1-Click Atomic Food Claims\n• Verified Handover Tracking\n• Unified Dual-Role Dashboard", PRIMARY_DARK, PRIMARY_GREEN),
        ("Target Users", "1. Food Providers:\n• Restaurants & Hotels\n• Banquet & Wedding Venues\n• College Mess & Caterers\n• Households & Stores\n\n2. Food Seekers:\n• NGOs & Charity Shelters\n• Community Kitchens\n• Volunteers & Individuals", TEXT_DARK, PRIMARY_DARK)
    ]

    for idx, (title, desc, header_col, accent_col) in enumerate(cards_data):
        c_left = left_margin + idx * (col_width + col_gap)
        c_shape = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left, top_pos, col_width, Inches(5.1))
        c_shape.fill.solid()
        c_shape.fill.fore_color.rgb = WHITE
        c_shape.line.color.rgb = BORDER_COLOR

        # Top Accent bar
        acc = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left, top_pos, col_width, Inches(0.12))
        acc.fill.solid()
        acc.fill.fore_color.rgb = accent_col
        acc.line.color.rgb = accent_col

        tx = s2.shapes.add_textbox(c_left + Inches(0.25), top_pos + Inches(0.3), col_width - Inches(0.5), Inches(4.5))
        tf = tx.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = header_col
        p.space_after = Pt(14)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK

    # =========================================================================
    # HELPER FUNCTION FOR SCREENSHOT SLIDES
    # =========================================================================
    def add_screenshot_slide(prs, title, category, img_path, bullets, badge="FEATURE"):
        slide = prs.slides.add_slide(blank_layout)
        add_header(slide, title, category)

        # Left Info Card
        card_w = Inches(4.6)
        card_h = Inches(5.5)
        card_l = Inches(0.8)
        card_t = Inches(1.4)

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_l, card_t, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER_COLOR

        tx = slide.shapes.add_textbox(card_l + Inches(0.3), card_t + Inches(0.3), card_w - Inches(0.6), card_h - Inches(0.6))
        tf = tx.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = f"FEATURE HIGHLIGHTS"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_GREEN
        p.space_after = Pt(10)

        for b_title, b_desc in bullets:
            p = tf.add_paragraph()
            p.text = f"• {b_title}"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = TEXT_DARK

            p2 = tf.add_paragraph()
            p2.text = f"   {b_desc}"
            p2.font.size = Pt(11)
            p2.font.color.rgb = TEXT_MUTED
            p2.space_after = Pt(8)

        # Right Screenshot Image Container
        img_l = Inches(5.65)
        img_t = Inches(1.4)
        img_w = Inches(6.88)
        img_h = Inches(5.5)

        # Background frame for screenshot
        frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, img_l, img_t, img_w, img_h)
        frame.fill.solid()
        frame.fill.fore_color.rgb = WHITE
        frame.line.color.rgb = BORDER_COLOR

        if os.path.exists(img_path):
            slide.shapes.add_picture(img_path, img_l + Inches(0.08), img_t + Inches(0.08), width=img_w - Inches(0.16), height=img_h - Inches(0.16))

        return slide

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE & TECH STACK
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "System Architecture & MongoDB NoSQL Design", "TECHNICAL ARCHITECTURE")

    # Left Column: Layered Stack
    stack_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.5))
    stack_box.fill.solid()
    stack_box.fill.fore_color.rgb = WHITE
    stack_box.line.color.rgb = BORDER_COLOR

    tx = s3.shapes.add_textbox(Inches(1.1), Inches(1.6), Inches(5.0), Inches(5.0))
    tf = tx.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Layered Architecture Breakdown"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_DARK
    p.space_after = Pt(10)

    layers = [
        ("Presentation Layer (Frontend)", "Pure semantic HTML5 & CSS3. No Bootstrap, Tailwind, or React. Ultra-fast, lightweight, responsive, and 100% offline-ready."),
        ("Application Layer (Django 6.1)", "Python 3.15 framework handling request routing, session lifecycle, view controllers, and PBKDF2 SHA-256 password security."),
        ("Database Service Layer (PyMongo)", "Official MongoDB driver handling connection pooling with automatic SSL/TLS certificate negotiation (certifi)."),
        ("Storage Layer (MongoDB Atlas NoSQL)", "Scalable document database with dynamic schema for flexible food attributes and atomic concurrency operations.")
    ]
    for name, desc in layers:
        p = tf.add_paragraph()
        p.text = f"✔ {name}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_after = Pt(6)

    # Right Column: Collections Schema
    schema_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.733), Inches(5.5))
    schema_box.fill.solid()
    schema_box.fill.fore_color.rgb = WHITE
    schema_box.line.color.rgb = BORDER_COLOR

    tx = s3.shapes.add_textbox(Inches(7.1), Inches(1.6), Inches(5.1), Inches(5.0))
    tf = tx.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "MongoDB Collections Schema (NoSQL)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_DARK
    p.space_after = Pt(10)

    colls = [
        ("users Collection", "• _id (ObjectId), username (unique)\n• email (unique), password (PBKDF2 hash)\n• full_name, phone, organization, address\n• default_role ('provider' | 'seeker')"),
        ("food_items Collection", "• _id, provider_id, provider_name, phone\n• title, description, category, food_type (Veg/Non-Veg)\n• quantity, pickup_address, pickup_time_slot\n• status ('available' | 'claimed' | 'collected')\n• claimed_by_id, claim_notes, collected_at"),
        ("claims Collection (Audit History)", "• _id, food_id, provider_id, seeker_id\n• seeker_name, seeker_phone, claim_time\n• Atomic concurrency audit logging")
    ]
    for cname, cfields in colls:
        p = tf.add_paragraph()
        p.text = f"📦 {cname}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_GREEN

        p2 = tf.add_paragraph()
        p2.text = cfields
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK
        p2.space_after = Pt(8)

    # =========================================================================
    # SLIDE 4: HOME LANDING PAGE
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Public Landing Page & Zero Hunger Mission",
        "USER INTERFACE",
        "screenshots/01_home_page.png",
        [
            ("Hero Banner & Call to Actions", "Clear gateway welcoming users with quick actions: Get Started, Browse Available Food, and Sign In."),
            ("Live Community Metrics", "Real-time counters directly connected to MongoDB: Available Listings, Total Meals Rescued, and Community Members."),
            ("Dual Role Showcase", "Explains the platform value for both Food Providers and Food Seekers in side-by-side structured cards."),
            ("Step-by-Step Workflow", "Visual 4-step workflow: Sign Up ➔ Post/Browse ➔ Claim & Coordinate ➔ Collect & Rescue.")
        ]
    )

    # =========================================================================
    # SLIDE 5: UNIFIED SIGNUP & ROLE SELECTION
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Unified Registration & Primary Role Intent",
        "AUTHENTICATION & ONBOARDING",
        "screenshots/02_signup_page.png",
        [
            ("Shared Single Sign-Up Flow", "Both Food Providers and Food Seekers register through one unified, intuitive registration portal."),
            ("Visual Role Card Selector", "Interactive radio cards allowing users to choose their primary intent: Food Provider (🍲) or Food Seeker (🤝)."),
            ("Comprehensive Profile Fields", "Captures Full Name, Unique Username, Email, Phone Number, Organization affiliation, and Pickup Address."),
            ("Validation & Password Safety", "Enforces password matching, minimum length, and unique indexes on MongoDB for username and email.")
        ]
    )

    # =========================================================================
    # SLIDE 6: SECURE UNIFIED LOGIN
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Unified Sign In & Cryptographic Security",
        "AUTHENTICATION & SECURITY",
        "screenshots/03_login_page.png",
        [
            ("Flexible Identifier Login", "Users can sign in using either their registered Username or Email address with their password."),
            ("PBKDF2 SHA-256 Verification", "Passwords are never stored in plaintext. They are verified against PBKDF2 cryptographic hashes."),
            ("Session Management", "Initializes a secure Django session tracking user ID, full name, email, and active mode."),
            ("Guest Browsing Access", "Direct shortcut link allowing guest visitors to browse available food before deciding to register.")
        ]
    )

    # =========================================================================
    # SLIDE 7: FOOD PROVIDER DASHBOARD
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Interactive Food Provider Dashboard",
        "PROVIDER EXPERIENCE",
        "screenshots/06_provider_dashboard.png",
        [
            ("Active Mode Banner & Switcher", "Prominently displays 'Active Mode: Food Provider' with a one-click toggle to switch to Seeker mode."),
            ("Provider KPI Metric Cards", "4 live counters: Total Food Listed, Currently Available, Pending Pickup, and Successfully Rescued."),
            ("Quick Action Tiles", "Instant navigation buttons to Add Food, View Food Catalog, Manage My Listings, and Account Settings."),
            ("Recent Donations Table", "Live table showing items listed, dietary badges (Veg/Non-Veg), status, claimer details, and quick view.")
        ]
    )

    # =========================================================================
    # SLIDE 8: ADD SURPLUS FOOD LISTING
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Surplus Food Listing Form",
        "FOOD DONATION WORKFLOW",
        "screenshots/07_add_food_form.png",
        [
            ("Detailed Food Categorization", "Dropdown for categories: Cooked Meals, Bakery, Fresh Produce, Packaged Food, Dairy, and Groceries."),
            ("Dietary Classification", "Veg, Non-Veg, and Vegan tags ensure recipients can respect dietary, religious, and health restrictions."),
            ("Logistics & Timing Fields", "Specifies precise Quantity (e.g. 35 servings), Pickup Address, City, Pickup Time Window, and Expiry info."),
            ("Profile Auto-Fill", "Automatically pre-populates contact person, phone number, and address from the provider's profile to save time.")
        ]
    )

    # =========================================================================
    # SLIDE 9: PROVIDER MY LISTINGS MANAGEMENT
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Provider Listings & Handover Management",
        "LIFECYCLE TRACKING",
        "screenshots/08_provider_my_listings.png",
        [
            ("End-to-End Status Tracking", "Color-coded status badges: Available (Green), Claimed / Pending Pickup (Amber), and Collected / Rescued (Blue)."),
            ("Seeker Coordination Details", "When an item is claimed, the seeker's name, phone number, and pickup notes appear immediately."),
            ("Mark Collected Action", "Providers can confirm physical food handover by clicking 'Mark Collected', recording the rescue."),
            ("Cancel / Delete Safeguard", "Allows canceling an available listing if circumstances change, automatically updating MongoDB.")
        ]
    )

    # =========================================================================
    # SLIDE 10: BROWSE & FILTER SURPLUS FOOD
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Surplus Food Discovery & Search Catalog",
        "SEEKER EXPERIENCE",
        "screenshots/04_view_food_catalog.png",
        [
            ("Multi-Parameter Filter Bar", "Instant search by dish name/location, category dropdown, dietary filter (Veg/Non-Veg), and city filter."),
            ("Informative Food Cards", "Displays dish title, description, category badge, quantity badge, pickup window, and expiry time."),
            ("Dynamic Pluralized Counter", "Accurate counter displaying the exact number of matching surplus listings currently available."),
            ("Zero Framework Lightweight CSS", "Pure CSS Grid layout that renders instantly on all mobile, tablet, and desktop viewports.")
        ]
    )

    # =========================================================================
    # SLIDE 11: FOOD DETAILS & ATOMIC CLAIMING
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Food Details & Atomic Concurrency Claim",
        "RESCUE ACTION",
        "screenshots/11_food_detail_view.png",
        [
            ("Comprehensive Food Specs", "Displays full description, dietary classification, quantity, preparation time, and best-before window."),
            ("Pickup & Provider Information", "Shows pickup address, landmark, provider organization, contact person, and direct call link."),
            ("Atomic Concurrency Protection", "Uses MongoDB's find_one_and_update to ensure no two seekers can claim the same meal simultaneously."),
            ("Seeker Pickup Notes", "Seekers can input estimated arrival time, vehicle info (e.g. NGO van), and team notes during claiming.")
        ]
    )

    # =========================================================================
    # SLIDE 12: FOOD SEEKER DASHBOARD
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Food Seeker Dashboard & Available Preview",
        "SEEKER DASHBOARD",
        "screenshots/12_seeker_dashboard.png",
        [
            ("Active Mode: Food Seeker", "Dashboard adapts to show seeker-centric capabilities, metrics, and active claims."),
            ("Seeker Rescue Statistics", "Summary cards showing Total Available in City, My Pending Claims, My Completed Pickups, and Total Claims."),
            ("Pending Claims Table", "Direct overview of claimed meals awaiting collection with provider phone numbers and pickup slots."),
            ("Available Food Preview Grid", "Real-time preview of the newest surplus donations ready to be claimed with a single click.")
        ]
    )

    # =========================================================================
    # SLIDE 13: SEEKER MY CLAIMS TRACKING
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Seeker Claims & Pickup Confirmation",
        "CLAIM MANAGEMENT",
        "screenshots/13_seeker_my_claims.png",
        [
            ("Comprehensive Claim History", "Lists all food items claimed by the seeker with quantities, provider details, and timestamps."),
            ("Direct Communication Link", "Click-to-call phone links for immediate coordination between volunteer driver and kitchen manager."),
            ("Confirm Pickup Action", "Volunteers or seekers can confirm successful collection upon receiving the food."),
            ("Historical Rescue Log", "Maintains a permanent audit record of all successfully distributed meals for NGO reporting.")
        ]
    )

    # =========================================================================
    # SLIDE 14: ACCOUNT SETTINGS & SECURITY
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Account Settings & Profile Management",
        "ACCOUNT MANAGEMENT",
        "screenshots/09_account_settings_profile.png",
        [
            ("Profile Details Update", "Allows editing Full Name, Email Address, Phone Number, Organization/Affiliation, and Default Address."),
            ("Default Mode Preference", "Users can change their preferred starting mode (Provider or Seeker) for future sessions."),
            ("Password Setting (Security)", "Old password verification combined with PBKDF2 cryptographic re-hashing for new passwords."),
            ("Delete Account (Danger Zone)", "Permanently deletes user account from MongoDB and cancels active listings after password confirmation.")
        ]
    )

    # =========================================================================
    # SLIDE 15: MONGODB DATABASE DIAGNOSTICS
    # =========================================================================
    add_screenshot_slide(
        prs,
        "Live MongoDB Atlas Diagnostics & Viva Notes",
        "DATABASE DIAGNOSTICS",
        "screenshots/05_database_status.png",
        [
            ("Real-Time Connection Check", "Live ping test displaying 'Connected & Healthy' status with MongoDB Atlas Cloud."),
            ("Live Document Counters", "Displays active counts for users, food_items, and claims collections directly from MongoDB."),
            ("College Viva Architectural Notes", "Highlights why NoSQL was chosen over Relational SQL: flexible schema, high write speed, and atomic updates."),
            ("Self-Healing Error Guidance", "If network or IP whitelist changes, diagnostic page displays 30-second fix instructions.")
        ]
    )

    # =========================================================================
    # SLIDE 16: CONCLUSION, IMPACT & FUTURE SCOPE
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "Project Summary, Impact & Future Roadmap", "CONCLUSION & FUTURE SCOPE")

    col_w = Inches(5.6)
    c1 = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), col_w, Inches(5.3))
    c1.fill.solid()
    c1.fill.fore_color.rgb = WHITE
    c1.line.color.rgb = BORDER_COLOR

    tx = s16.shapes.add_textbox(Inches(1.1), Inches(1.8), col_w - Inches(0.6), Inches(4.8))
    tf = tx.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Key Project Achievements"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_DARK
    p.space_after = Pt(12)

    points1 = [
        ("Clean Django Architecture", "Built on Django 6.1 & Python 3.15 with clean separation of models, business logic, auth helpers, and views."),
        ("Robust MongoDB NoSQL Integration", "Direct integration with MongoDB Atlas Cloud utilizing PyMongo with automatic SSL/TLS root certificates."),
        ("Atomic Concurrency Safety", "Race-condition prevention ensures multiple seekers never claim the same surplus food item."),
        ("Pure HTML5/CSS3 UI", "Zero bloated JavaScript frameworks or CDN dependencies. Fully responsive, professional, and college-ready."),
        ("14 Passing Automated Tests", "Comprehensive test suite verifying authentication, atomic claim logic, and view responses.")
    ]
    for pt, pd in points1:
        p = tf.add_paragraph()
        p.text = f"✔ {pt}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p2 = tf.add_paragraph()
        p2.text = f"   {pd}"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_after = Pt(4)

    c2 = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), col_w + Inches(0.133), Inches(5.3))
    c2.fill.solid()
    c2.fill.fore_color.rgb = WHITE
    c2.line.color.rgb = BORDER_COLOR

    tx2 = s16.shapes.add_textbox(Inches(7.1), Inches(1.8), col_w - Inches(0.4), Inches(4.8))
    tf2 = tx2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "Future Scope & Enhancements"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_DARK
    p.space_after = Pt(12)

    points2 = [
        ("Geolocation & Map Routing", "Integrate OpenStreetMap or Google Maps for live route optimization between provider and volunteer drivers."),
        ("SMS & WhatsApp Notifications", "Send automated pickup alerts and reminders to volunteers via Twilio or WhatsApp Business API."),
        ("AI Food Spoilage Estimator", "Computer vision model to estimate freshness and remaining shelf life of cooked meals from photos."),
        ("Volunteer Fleet Coordination", "Dispatch delivery tasks to community volunteers for large wedding banquets and corporate events.")
    ]
    for pt, pd in points2:
        p = tf2.add_paragraph()
        p.text = f"🚀 {pt}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p2 = tf2.add_paragraph()
        p2.text = f"   {pd}"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_after = Pt(6)

    output_path = "Food_Rescue_Management_System_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_deck()
