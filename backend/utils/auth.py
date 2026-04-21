from datetime import datetime, timedelta
from bson import ObjectId
import secrets
from werkzeug.security import generate_password_hash, check_password_hash as werkzeug_check
try:
    from flask_bcrypt import check_password_hash as bcrypt_check
except ImportError:
    # Fallback if flask-bcrypt is not available
    bcrypt_check = None
from utils.db import users_collection, history_collection

RETENTION_DAYS = 3
RETENTION_DELTA = timedelta(days=RETENTION_DAYS)


def cleanup_expired_history(user_id):
    history_collection.delete_many({
        "user_id": ObjectId(user_id),
        "retention_expires_at": {"$lte": datetime.utcnow()},
    })


def normalize_credential(value):
    return value.strip() if isinstance(value, str) else value

def create_user(username, email, password):
    username = normalize_credential(username)
    email = normalize_credential(email)
    password = normalize_credential(password)

    if users_collection.find_one({'$or': [{'username': username}, {'email': email}]}):
        return None, "User already exists"

    # Use fast pbkdf2 provided by werkzeug
    pw_hash = generate_password_hash(password)
    api_key = f"sk_live_{secrets.token_hex(16)}"
    
    new_user = {
        "username": username,
        "email": email,
        "password_hash": pw_hash,
        "api_key": api_key,
        "settings": {
            "storage_threshold": 60,
            "auto_flag": False
        },
        "created_at": datetime.utcnow()
    }
    
    res = users_collection.insert_one(new_user)
    new_user["_id"] = str(res.inserted_id)
    return new_user, None

def verify_user(username_or_email, password):
    username_or_email = normalize_credential(username_or_email)
    password = normalize_credential(password)

    user = users_collection.find_one({
        '$or': [{'username': username_or_email}, {'email': username_or_email}]
    })
    
    if user:
        pwd_hash = user['password_hash']
        is_valid = False
        
        # Check if the hash is an old bcrypt hash
        if pwd_hash.startswith('$2b$') and bcrypt_check:
            is_valid = bcrypt_check(pwd_hash, password)
            if is_valid:
                # Upgrade hash dynamically for future fast logins
                new_hash = generate_password_hash(password)
                users_collection.update_one(
                    {"_id": user['_id']},
                    {"$set": {"password_hash": new_hash}}
                )
        else:
            is_valid = werkzeug_check(pwd_hash, password)
            
        if is_valid:
            user['_id'] = str(user['_id'])
            return user
            
    return None

def get_user_by_id(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user['_id'] = str(user['_id'])
    return user

def get_user_by_api_key(api_key):
    user = users_collection.find_one({"api_key": api_key})
    if user:
        user['_id'] = str(user['_id'])
    return user

def save_scan_history(user_id, text, score, verdict, source, details, storage_threshold=60):
    try:
        threshold_value = max(0, min(100, int(storage_threshold)))
    except (TypeError, ValueError):
        threshold_value = 60

    created_at = datetime.utcnow()
    doc = {
        "user_id": ObjectId(user_id) if user_id else None,
        "text_snippet": text[:100] + "..." if len(text) > 100 else text,
        "full_text": text,
        "risk_score": score,
        "verdict": verdict,
        "source": source,
        "analysis_details": details,
        "timestamp": created_at,
        "storage_threshold": threshold_value,
    }

    if score < threshold_value:
        doc["retention_expires_at"] = created_at + RETENTION_DELTA

    res = history_collection.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    if doc.get("user_id"):
        doc["user_id"] = str(doc["user_id"])
    return doc

def get_user_history(user_id, limit=50):
    cleanup_expired_history(user_id)
    cursor = history_collection.find({"user_id": ObjectId(user_id)}).sort("timestamp", -1).limit(limit)
    history = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["user_id"])
        history.append(doc)
    return history

def update_user_settings(user_id, new_settings):
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"settings": new_settings}}
    )


def update_user_profile(user_id, username=None, email=None):
    updates = {}

    if isinstance(username, str) and username.strip():
        updates["username"] = username.strip()
    if isinstance(email, str) and email.strip():
        updates["email"] = email.strip()

    if not updates:
        return None, "No profile fields to update"

    duplicate_query = []
    if "username" in updates:
        duplicate_query.append({"username": updates["username"]})
    if "email" in updates:
        duplicate_query.append({"email": updates["email"]})

    if duplicate_query:
        existing = users_collection.find_one(
            {
                "$and": [
                    {"_id": {"$ne": ObjectId(user_id)}},
                    {"$or": duplicate_query},
                ]
            }
        )
        if existing:
            return None, "Username or email already in use"

    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    updated_user = get_user_by_id(user_id)
    return updated_user, None


def change_user_password(user_id, current_password, new_password):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False, "User not found"

    current_password = normalize_credential(current_password)
    new_password = normalize_credential(new_password)

    if not current_password or not new_password:
        return False, "Missing required fields"

    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"

    pwd_hash = user.get("password_hash", "")
    valid_current = False
    if pwd_hash.startswith('$2b$') and bcrypt_check:
        valid_current = bcrypt_check(pwd_hash, current_password)
    else:
        valid_current = werkzeug_check(pwd_hash, current_password)

    if not valid_current:
        return False, "Current password is incorrect"

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": generate_password_hash(new_password)}}
    )
    return True, None


def verify_user_password(user_id, password):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False, "User not found"

    password = normalize_credential(password)
    if not password:
        return False, "Password is required"

    pwd_hash = user.get("password_hash", "")
    if pwd_hash.startswith('$2b$') and bcrypt_check:
        is_valid = bcrypt_check(pwd_hash, password)
    else:
        is_valid = werkzeug_check(pwd_hash, password)

    if not is_valid:
        return False, "Current password is incorrect"

    return True, None
