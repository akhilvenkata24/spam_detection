import os
from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from datetime import datetime, timedelta

# Use MONGO_URL if available, otherwise MONGO_URI, fallback to localhost.
# The explicit `or` fallback avoids treating an empty env var as a valid URI.
MONGO_URI = os.getenv("MONGO_URL") or os.getenv("MONGO_URI") or "mongodb://localhost:27017"
DB_NAME = "spam_detection_db"

def _is_placeholder_uri(uri: str) -> bool:
    tokenized = uri.lower()
    return "<" in tokenized or ">" in tokenized or "replace-with" in tokenized


def _create_client() -> MongoClient:
    uri = MONGO_URI.strip()

    # Guard against copied template values like mongodb+srv://<username>:<password>@<cluster>/...
    if _is_placeholder_uri(uri):
        print("Warning: Placeholder Mongo URI detected. Falling back to mongodb://localhost:27017")
        uri = "mongodb://localhost:27017"

    try:
        return MongoClient(uri, serverSelectionTimeoutMS=5000)
    except ConfigurationError as e:
        # Invalid SRV/DNS configuration should not crash app startup in local dev.
        print(f"Warning: Invalid Mongo URI '{uri}'. Falling back to localhost. Details: {e}")
        return MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)


client = _create_client()
db = client[DB_NAME]

users_collection = db["users"]
history_collection = db["scan_history"]
sms_collection = db["sms_messages"]

try:
    # Create indexes for performance
    users_collection.create_index("username", unique=True)
    users_collection.create_index("email", unique=True)
    users_collection.create_index("api_key", unique=True)
    history_collection.create_index("user_id")
    history_collection.create_index([("timestamp", -1)])
    history_collection.create_index([("retention_expires_at", 1)], expireAfterSeconds=0)
    sms_collection.create_index("user_id")
    sms_collection.create_index([("date", -1)])
    sms_collection.create_index([("retention_expires_at", 1)], expireAfterSeconds=0)

    def _parse_dt(value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                return None
        return None

    for doc in history_collection.find({}):
        threshold = int(doc.get("storage_threshold", 60) or 60)
        risk_score = int(doc.get("risk_score", 0) or 0)
        timestamp = _parse_dt(doc.get("timestamp"))
        if risk_score < threshold and timestamp:
            history_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"storage_threshold": threshold, "retention_expires_at": timestamp + timedelta(days=3)}},
            )
        else:
            history_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"storage_threshold": threshold}, "$unset": {"retention_expires_at": ""}},
            )

    for doc in sms_collection.find({}):
        threshold = int(doc.get("storage_threshold", 60) or 60)
        risk_score = int(doc.get("risk_score", 0) or 0)
        imported_at = _parse_dt(doc.get("imported_at"))
        if risk_score < threshold and imported_at:
            sms_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"storage_threshold": threshold, "retention_expires_at": imported_at + timedelta(days=3)}},
            )
        else:
            sms_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"storage_threshold": threshold}, "$unset": {"retention_expires_at": ""}},
            )
    print("MongoDB indices verified.")
except Exception as e:
    print(f"Warning: MongoDB connection or index creation failed: {e}")
