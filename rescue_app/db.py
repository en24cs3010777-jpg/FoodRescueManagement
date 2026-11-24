"""
MongoDB Connection and Database Management Module.
Provides thread-safe access to MongoDB collections using PyMongo.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson.objectid import ObjectId
from django.conf import settings
import logging

try:
    import certifi
    CA_FILE = certifi.where()
except ImportError:
    CA_FILE = None

logger = logging.getLogger(__name__)

# Global client cache
_mongo_client = None


def get_client():
    """Returns a singleton MongoClient instance."""
    global _mongo_client
    if _mongo_client is None:
        uri = getattr(settings, 'MONGO_URI', 'mongodb://localhost:27017/')
        client_kwargs = {
            'serverSelectionTimeoutMS': 5000,
            'connectTimeoutMS': 5000,
        }
        if CA_FILE and ('mongodb+srv://' in uri or 'ssl=true' in uri.lower()):
            client_kwargs['tlsCAFile'] = CA_FILE

        _mongo_client = MongoClient(uri, **client_kwargs)
    return _mongo_client


def get_db():
    """Returns the application MongoDB database instance."""
    client = get_client()
    db_name = getattr(settings, 'MONGO_DB_NAME', 'food_rescue_db')
    return client[db_name]


def check_db_connection():
    """
    Tests if MongoDB is reachable.
    Returns:
        (bool, str or None): (True, None) on success, or (False, error_message) on failure.
    """
    try:
        client = get_client()
        client.admin.command('ping')
        return True, None
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        logger.warning(f"MongoDB connection failed: {exc}")
        return False, str(exc)
    except Exception as exc:
        logger.error(f"Unexpected MongoDB error: {exc}")
        return False, str(exc)


def get_users_collection():
    """Returns the 'users' collection."""
    return get_db()['users']


def get_food_collection():
    """Returns the 'food_items' collection."""
    return get_db()['food_items']


def get_claims_collection():
    """Returns the 'claims' collection."""
    return get_db()['claims']


def init_indexes():
    """
    Initializes indexes for performance and data integrity:
    - Unique indexes on users (username, email)
    - Query indexes on food items (status, provider, date)
    """
    try:
        users = get_users_collection()
        users.create_index("username", unique=True)
        users.create_index("email", unique=True)

        food = get_food_collection()
        food.create_index([("status", ASCENDING), ("created_at", DESCENDING)])
        food.create_index("provider_id")
        food.create_index("claimed_by_id")

        claims = get_claims_collection()
        claims.create_index("food_id")
        claims.create_index("seeker_id")
        return True
    except Exception as exc:
        logger.warning(f"Could not initialize indexes: {exc}")
        return False


def to_object_id(id_val):
    """
    Safely converts a string to a BSON ObjectId.
    Returns ObjectId or None if invalid.
    """
    if not id_val:
        return None
    if isinstance(id_val, ObjectId):
        return id_val
    try:
        return ObjectId(str(id_val))
    except Exception:
        return None


def serialize_doc(doc):
    """
    Helper to prepare a MongoDB document for Django templates:
    Converts ObjectId `_id` to string `id` while preserving other fields.
    """
    if not doc:
        return None
    doc_copy = dict(doc)
    if '_id' in doc_copy:
        doc_copy['id'] = str(doc_copy['_id'])
    return doc_copy
