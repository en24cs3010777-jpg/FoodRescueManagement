"""
Views for Food Rescue Management System.
Handles user authentication, dashboard mode toggling, food listing & claiming,
and comprehensive account settings.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

from rescue_app.db import check_db_connection, get_db, init_indexes
from rescue_app.auth_helper import (
    create_user,
    authenticate_user,
    get_user_by_id,
    update_user_profile,
    update_user_password,
    delete_user_account,
    login_required_mongo
)
from rescue_app.food_service import (
    FOOD_CATEGORIES,
    FOOD_TYPES,
    add_food_item,
    get_available_food_items,
    get_food_item_by_id,
    claim_food_item,
    mark_food_collected,
    cancel_food_item,
    get_provider_listings,
    get_seeker_claims,
    get_dashboard_stats
)


def home_view(request):
    """Public home landing page introducing the Food Rescue platform."""
    if request.session.get('user_id'):
        return redirect('dashboard')

    is_db_ok, db_err = check_db_connection()
    stats = {
        "available_food": 0,
        "rescued_food": 0,
        "active_users": 0
    }
    if is_db_ok:
        try:
            db = get_db()
            stats["available_food"] = db['food_items'].count_documents({"status": "available"})
            stats["rescued_food"] = db['food_items'].count_documents({"status": "collected"})
            stats["active_users"] = db['users'].count_documents({})
        except Exception:
            pass

    return render(request, 'home.html', {
        'stats': stats,
        'db_ok': is_db_ok,
        'db_err': db_err
    })


def signup_view(request):
    """
    Unified registration for both Food Providers and Food Seekers.
    Users can select their primary role, but both roles share the same platform.
    """
    if request.session.get('user_id'):
        return redirect('dashboard')

    is_db_ok, db_err = check_db_connection()
    if not is_db_ok:
        return render(request, 'db_error.html', {'error': db_err})

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', 'provider')
        organization = request.POST.get('organization', '').strip()
        address = request.POST.get('address', '').strip()

        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'signup.html', {
                'form_data': request.POST
            })

        user, err = create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
            role=role,
            organization=organization,
            address=address
        )

        if err:
            messages.error(request, err)
            return render(request, 'signup.html', {
                'form_data': request.POST
            })

        # Initialize indexes on first user signup
        init_indexes()

        # Log user in directly
        request.session['user_id'] = user['id']
        request.session['username'] = user['username']
        request.session['full_name'] = user['full_name']
        request.session['email'] = user['email']
        request.session['active_mode'] = user.get('default_role', 'provider')

        messages.success(request, f"Welcome to Food Rescue, {user['full_name']}! Your account has been created.")
        return redirect('dashboard')

    return render(request, 'signup.html', {'form_data': {}})


def login_view(request):
    """Unified login for all users (Providers & Seekers)."""
    if request.session.get('user_id'):
        return redirect('dashboard')

    is_db_ok, db_err = check_db_connection()
    if not is_db_ok:
        return render(request, 'db_error.html', {'error': db_err})

    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate_user(username_or_email, password)
        if not user:
            messages.error(request, "Invalid username/email or password. Please try again.")
            return render(request, 'login.html', {'username_or_email': username_or_email})

        # Set session
        request.session['user_id'] = user['id']
        request.session['username'] = user['username']
        request.session['full_name'] = user['full_name']
        request.session['email'] = user['email']
        request.session['active_mode'] = user.get('default_role', 'provider')

        messages.success(request, f"Welcome back, {user['full_name']}!")
        return redirect('dashboard')

    return render(request, 'login.html')


def logout_view(request):
    """Logs out the user and clears session."""
    request.session.flush()
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required_mongo
def switch_mode_view(request, mode):
    """
    Switches active role mode between 'provider' (Provide Food) and 'seeker' (Seek Food).
    """
    if mode in ('provider', 'seeker'):
        request.session['active_mode'] = mode
        mode_label = "Food Provider" if mode == 'provider' else "Food Seeker"
        messages.success(request, f"Switched active mode to {mode_label}.")
    return redirect('dashboard')


@login_required_mongo
def dashboard_view(request):
    """
    Main user dashboard.
    Prominently displays current mode (Provider or Seeker) and allows switching.
    Shows mode-relevant statistics, quick actions, and recent activity.
    """
    user = request.mongo_user
    active_mode = request.session.get('active_mode', user.get('default_role', 'provider'))

    stats = get_dashboard_stats(user['id'], active_mode)

    context = {
        'user': user,
        'active_mode': active_mode,
        'stats': stats,
    }

    if active_mode == 'provider':
        my_listings = get_provider_listings(user['id'])
        context['recent_listings'] = my_listings[:5]
        context['total_listings_count'] = len(my_listings)
    else:  # seeker mode
        my_claims = get_seeker_claims(user['id'])
        available_food = get_available_food_items()
        context['recent_claims'] = my_claims[:5]
        context['available_food_preview'] = available_food[:6]
        context['total_claims_count'] = len(my_claims)

    return render(request, 'dashboard.html', context)


@login_required_mongo
def add_food_view(request):
    """Food Provider: Add new surplus food listing."""
    user = request.mongo_user

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'Cooked Meals')
        food_type = request.POST.get('food_type', 'Vegetarian')
        quantity = request.POST.get('quantity', '').strip()
        pickup_address = request.POST.get('pickup_address', '').strip()
        pickup_city = request.POST.get('pickup_city', '').strip()
        pickup_time_slot = request.POST.get('pickup_time_slot', '').strip()
        expiry_info = request.POST.get('expiry_info', '').strip()
        contact_person = request.POST.get('contact_person', user.get('full_name', '')).strip()
        contact_phone = request.POST.get('contact_phone', user.get('phone', '')).strip()

        food, err = add_food_item(
            provider_user=user,
            title=title,
            description=description,
            category=category,
            food_type=food_type,
            quantity=quantity,
            pickup_address=pickup_address,
            pickup_city=pickup_city,
            pickup_time_slot=pickup_time_slot,
            expiry_info=expiry_info,
            contact_person=contact_person,
            contact_phone=contact_phone
        )

        if err:
            messages.error(request, err)
            return render(request, 'add_food.html', {
                'categories': FOOD_CATEGORIES,
                'food_types': FOOD_TYPES,
                'form_data': request.POST
            })

        messages.success(request, f"Food listing '{food['title']}' added successfully! It is now visible to food seekers.")
        return redirect('my_listings')

    # Pre-populate defaults from user profile
    initial_data = {
        'pickup_address': user.get('address', ''),
        'contact_person': user.get('full_name', ''),
        'contact_phone': user.get('phone', '')
    }

    return render(request, 'add_food.html', {
        'categories': FOOD_CATEGORIES,
        'food_types': FOOD_TYPES,
        'form_data': initial_data
    })


def view_food_view(request):
    """
    Public and seeker browsing view for all available surplus food items.
    Supports search query, category filter, dietary filter, and city filter.
    """
    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', 'All')
    selected_food_type = request.GET.get('food_type', 'All')
    selected_city = request.GET.get('city', '').strip()

    try:
        items = get_available_food_items(
            search_query=search_query,
            category=selected_category,
            food_type=selected_food_type,
            city=selected_city
        )
    except Exception as exc:
        return render(request, 'db_error.html', {'error': str(exc)})

    return render(request, 'view_food.html', {
        'food_items': items,
        'categories': ["All"] + FOOD_CATEGORIES,
        'food_types': ["All"] + FOOD_TYPES,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_food_type': selected_food_type,
        'selected_city': selected_city,
        'total_count': len(items)
    })


def food_detail_view(request, food_id):
    """Displays detailed information for a single food item with claim action."""
    try:
        item = get_food_item_by_id(food_id)
    except Exception as exc:
        return render(request, 'db_error.html', {'error': str(exc)})

    if not item:
        messages.error(request, "Food listing not found.")
        return redirect('view_food')

    current_user_id = request.session.get('user_id')
    is_owner = (current_user_id and str(item.get('provider_id')) == str(current_user_id))
    is_claimed_by_me = (current_user_id and str(item.get('claimed_by_id')) == str(current_user_id))

    return render(request, 'food_detail.html', {
        'item': item,
        'is_owner': is_owner,
        'is_claimed_by_me': is_claimed_by_me,
    })


@login_required_mongo
@require_POST
def claim_food_view(request, food_id):
    """Food Seeker: Claims an available food item."""
    user = request.mongo_user
    claim_notes = request.POST.get('claim_notes', '').strip()

    success, msg = claim_food_item(food_id, user, claim_notes=claim_notes)
    if success:
        messages.success(request, msg)
        return redirect('my_claims')
    else:
        messages.error(request, msg)
        return redirect('food_detail', food_id=food_id)


@login_required_mongo
@require_POST
def mark_collected_view(request, food_id):
    """Marks a food listing as successfully collected / rescued."""
    user = request.mongo_user
    success, msg = mark_food_collected(food_id, user['id'])

    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)

    # Return to referring page or dashboard
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'dashboard'
    return redirect(next_url)


@login_required_mongo
@require_POST
def cancel_food_view(request, food_id):
    """Food Provider: Cancels or deletes a food listing."""
    user = request.mongo_user
    success, msg = cancel_food_item(food_id, user['id'])

    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)

    return redirect('my_listings')


@login_required_mongo
def my_listings_view(request):
    """Food Provider: Management view of all food listings posted by the user."""
    user = request.mongo_user
    listings = get_provider_listings(user['id'])

    return render(request, 'my_listings.html', {
        'listings': listings,
        'total_count': len(listings),
    })


@login_required_mongo
def my_claims_view(request):
    """Food Seeker: Management view of all food items claimed/collected by the user."""
    user = request.mongo_user
    claims = get_seeker_claims(user['id'])

    return render(request, 'my_claims.html', {
        'claims': claims,
        'total_count': len(claims),
    })


@login_required_mongo
def account_settings_view(request):
    """
    Account Settings page featuring:
    1. Profile update (Name, Email, Phone, Organization, Address, Default Role)
    2. Password update (Old Password, New Password, Confirm Password)
    3. Account deletion with confirmation
    """
    user = request.mongo_user
    active_tab = 'profile'

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            active_tab = 'profile'
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            organization = request.POST.get('organization', '').strip()
            address = request.POST.get('address', '').strip()
            default_role = request.POST.get('default_role', 'provider')

            success, msg = update_user_profile(
                user_id=user['id'],
                full_name=full_name,
                email=email,
                phone=phone,
                organization=organization,
                address=address,
                default_role=default_role
            )

            if success:
                # Update session
                request.session['full_name'] = full_name
                request.session['email'] = email
                messages.success(request, msg)
                return redirect('account_settings')
            else:
                messages.error(request, msg)

        elif action == 'change_password':
            active_tab = 'password'
            old_password = request.POST.get('old_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            success, msg = update_user_password(
                user_id=user['id'],
                old_password=old_password,
                new_password=new_password,
                confirm_password=confirm_password
            )

            if success:
                messages.success(request, msg)
                return redirect('account_settings')
            else:
                messages.error(request, msg)

        elif action == 'delete_account':
            active_tab = 'delete'
            password_confirm = request.POST.get('delete_password', '')

            success, msg = delete_user_account(user['id'], password_confirm)
            if success:
                request.session.flush()
                messages.success(request, "Your account has been deleted. We are sorry to see you go!")
                return redirect('home')
            else:
                messages.error(request, msg)

    # Re-fetch user to display latest data
    fresh_user = get_user_by_id(user['id']) or user

    return render(request, 'account_settings.html', {
        'user': fresh_user,
        'active_tab': active_tab
    })


def db_status_view(request):
    """Helper diagnostic view showing MongoDB connection status & database info."""
    is_ok, err = check_db_connection()
    details = {
        'connected': is_ok,
        'error': err,
        'database_name': None,
        'collections': [],
        'users_count': 0,
        'food_items_count': 0,
        'claims_count': 0,
    }

    if is_ok:
        try:
            db = get_db()
            details['database_name'] = db.name
            details['collections'] = db.list_collection_names()
            details['users_count'] = db['users'].count_documents({})
            details['food_items_count'] = db['food_items'].count_documents({})
            details['claims_count'] = db['claims'].count_documents({})
        except Exception as exc:
            details['connected'] = False
            details['error'] = str(exc)

    return render(request, 'db_status.html', {'status': details})
