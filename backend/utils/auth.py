from datetime import datetime
from bson import ObjectId
import secrets
from flask_bcrypt import generate_password_hash, check_password_hash
from utils.db import users_collection, history_collection

def create_user(username, email, password):
    if users_collection.find_one({'$or': [{'username': username}, {'email': email}]}):
        return None, "User already exists"

    pw_hash = generate_password_hash(password).decode('utf-8')
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
    user = users_collection.find_one({
        '$or': [{'username': username_or_email}, {'email': username_or_email}]
    })
    if user and check_password_hash(user['password_hash'], password):
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

def save_scan_history(user_id, text, score, verdict, source, details):
    doc = {
        "user_id": ObjectId(user_id) if user_id else None,
        "text_snippet": text[:100] + "..." if len(text) > 100 else text,
        "risk_score": score,
        "verdict": verdict,
        "source": source,
        "analysis_details": details,
        "timestamp": datetime.utcnow()
    }
    res = history_collection.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    if doc.get("user_id"):
        doc["user_id"] = str(doc["user_id"])
    return doc

def get_user_history(user_id, limit=50):
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
