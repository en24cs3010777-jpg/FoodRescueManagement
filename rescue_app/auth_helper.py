"""
Authentication and User Account Management for MongoDB.
Handles secure password hashing, user registration, authentication, and session decorators.
"""

from functools import wraps
from datetime import datetime, timezone
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from rescue_app.db import get_users_collection, to_object_id, serialize_doc


def create_user(username, email, password, full_name, phone, role='provider', organization='', address=''):
    """
    Registers a new user in MongoDB.
    Returns:
        (user_doc, None) on success, or (None, error_message) on failure.
    """
    username = username.strip().lower()
    email = email.strip().lower()
    full_name = full_name.strip()
    phone = phone.strip()
    role = role.strip().lower()
    if role not in ('provider', 'seeker'):
        role = 'provider'

    if not username or len(username) < 3:
        return None, "Username must be at least 3 characters long."
    if not email or '@' not in email:
        return None, "Please enter a valid email address."
    if not password or len(password) < 6:
        return None, "Password must be at least 6 characters long."
    if not full_name:
        return None, "Full name is required."

    users = get_users_collection()

    # Check duplicate username
    if users.find_one({"username": username}):
        return None, f"Username '{username}' is already taken. Please choose another."

    # Check duplicate email
    if users.find_one({"email": email}):
        return None, f"An account with email '{email}' already exists."

    now = datetime.now(timezone.utc)
    user_doc = {
        "username": username,
        "email": email,
        "password": make_password(password),
        "full_name": full_name,
        "phone": phone,
        "default_role": role,  # 'provider' or 'seeker'
        "organization": organization.strip(),
        "address": address.strip(),
        "created_at": now,
        "updated_at": now,
    }

    result = users.insert_one(user_doc)
    user_doc['_id'] = result.inserted_id
    return serialize_doc(user_doc), None


def authenticate_user(username_or_email, password):
    """
    Validates user credentials against MongoDB.
    Returns user doc if valid, otherwise None.
    """
    if not username_or_email or not password:
        return None

    identifier = username_or_email.strip().lower()
    users = get_users_collection()

    # Look up by username or email
    user = users.find_one({
        "$or": [
            {"username": identifier},
            {"email": identifier}
        ]
    })

    if not user:
        return None

    if check_password(password, user.get('password', '')):
        return serialize_doc(user)

    return None


def get_user_by_id(user_id):
    """Fetches user document by string ID or ObjectId."""
    oid = to_object_id(user_id)
    if not oid:
        return None
    users = get_users_collection()
    user = users.find_one({"_id": oid})
    return serialize_doc(user)


def update_user_profile(user_id, full_name, email, phone, organization, address, default_role=None):
    """
    Updates profile details in MongoDB.
    Returns: (success_bool, message)
    """
    oid = to_object_id(user_id)
    if not oid:
        return False, "Invalid user identifier."

    users = get_users_collection()
    email = email.strip().lower()

    # Check if updated email conflicts with another user
    existing = users.find_one({"email": email, "_id": {"$ne": oid}})
    if existing:
        return False, "This email is already registered to another account."

    update_fields = {
        "full_name": full_name.strip(),
        "email": email,
        "phone": phone.strip(),
        "organization": organization.strip(),
        "address": address.strip(),
        "updated_at": datetime.now(timezone.utc),
    }

    if default_role in ('provider', 'seeker'):
        update_fields["default_role"] = default_role

    users.update_one({"_id": oid}, {"$set": update_fields})
    return True, "Profile updated successfully."


def update_user_password(user_id, old_password, new_password, confirm_password):
    """
    Validates old password and sets new password.
    Returns: (success_bool, message)
    """
    oid = to_object_id(user_id)
    if not oid:
        return False, "Invalid user identifier."

    if not new_password or len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    if new_password != confirm_password:
        return False, "New password and confirmation do not match."

    users = get_users_collection()
    user = users.find_one({"_id": oid})
    if not user:
        return False, "User not found."

    if not check_password(old_password, user.get('password', '')):
        return False, "Incorrect current password."

    hashed = make_password(new_password)
    users.update_one(
        {"_id": oid},
        {"$set": {"password": hashed, "updated_at": datetime.now(timezone.utc)}}
    )
    return True, "Password changed successfully."


def delete_user_account(user_id, password_confirm):
    """
    Permanently deletes user account and cancels active food listings.
    Requires password confirmation for safety.
    Returns: (success_bool, message)
    """
    oid = to_object_id(user_id)
    if not oid:
        return False, "Invalid user identifier."

    users = get_users_collection()
    user = users.find_one({"_id": oid})
    if not user:
        return False, "User account not found."

    if not check_password(password_confirm, user.get('password', '')):
        return False, "Incorrect password. Account deletion aborted."

    # Clean up or mark cancelled pending listings
    from rescue_app.db import get_food_collection
    food_coll = get_food_collection()
    food_coll.update_many(
        {"provider_id": str(oid), "status": "available"},
        {"$set": {"status": "cancelled", "notes": "Provider account deleted"}}
    )

    users.delete_one({"_id": oid})
    return True, "Account deleted successfully."


def login_required_mongo(view_func):
    """
    Decorator for views that checks if user is logged into the session.
    Injects request.mongo_user with the user profile doc.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.warning(request, "Please log in to access this page.")
            return redirect('login')

        try:
            user = get_user_by_id(user_id)
        except Exception as exc:
            return render(request, 'db_error.html', {'error': str(exc)})

        if not user:
            # Session exists but user deleted or invalid
            request.session.flush()
            messages.error(request, "User session expired. Please log in again.")
            return redirect('login')

        # Attach user to request object
        request.mongo_user = user
        try:
            return view_func(request, *args, **kwargs)
        except Exception as exc:
            from pymongo.errors import PyMongoError
            if isinstance(exc, PyMongoError) or 'SSL' in str(exc) or 'mongo' in str(exc).lower():
                return render(request, 'db_error.html', {'error': str(exc)})
            raise

    return _wrapped_view
