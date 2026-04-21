from datetime import datetime, timedelta
from bson import ObjectId
from utils.db import sms_collection

RETENTION_DAYS = 3
RETENTION_DELTA = timedelta(days=RETENTION_DAYS)


def cleanup_expired_sms(user_id):
    sms_collection.delete_many({
        "user_id": ObjectId(user_id),
        "retention_expires_at": {"$lte": datetime.utcnow()},
    })


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return None
    return None

def save_user_sms(user_id, messages_list, storage_threshold=60):
    if not messages_list:
        return []

    docs = []
    user_obj_id = ObjectId(user_id) if user_id else None
    or_conditions = []
    try:
        threshold_value = max(0, min(100, int(storage_threshold)))
    except (TypeError, ValueError):
        threshold_value = 60
    
    for msg in messages_list:
        sender = msg.get("sender", "unknown")
        body = msg.get("body", "")
        msg_date = msg.get("date", datetime.utcnow())
        msg_date = _parse_datetime(msg_date) or datetime.utcnow()

        # Condition to find previous occurrence
        or_conditions.append({
            "sender": sender,
            "body": body,
            "date": msg_date
        })

        doc = {
            "user_id": user_obj_id,
            "sender": sender,
            "body": body,
            "date": msg_date,
            "is_spam": msg.get("is_spam", False),
            "risk_score": msg.get("risk_score", 0),
            "verdict": msg.get("verdict", "high_risk" if msg.get("is_spam", False) else "safe"),
            "source": msg.get("source", "Mobile SMS Sync"),
            "imported_at": datetime.utcnow(),
            "storage_threshold": threshold_value,
        }

        if doc["risk_score"] < threshold_value:
            doc["retention_expires_at"] = doc["imported_at"] + RETENTION_DELTA

        docs.append(doc)
    
    if docs:
        # Delete previous occurrences to prevent duplication
        # Batching deletions up to 1000 items at a time to avoid BSON size limits
        for i in range(0, len(or_conditions), 1000):
            batch_conditions = or_conditions[i:i+1000]
            sms_collection.delete_many({
                "user_id": user_obj_id,
                "$or": batch_conditions
            })

        sms_collection.insert_many(docs)
    
    return docs

def format_doc(doc):
    doc["_id"] = str(doc["_id"])
    if doc.get("user_id"):
        doc["user_id"] = str(doc["user_id"])
    
    for key in ("imported_at", "date"):
        value = doc.get(key)
        if isinstance(value, datetime):
            doc[key] = value.isoformat() + "Z"
        
    return doc

def get_user_sms(user_id):
    cleanup_expired_sms(user_id)
    cursor = sms_collection.find({"user_id": ObjectId(user_id)}).sort("imported_at", -1)
    messages = []
    for doc in cursor:
        messages.append(format_doc(doc))
    return messages

def get_spam_sms(user_id):
    cursor = sms_collection.find({"user_id": ObjectId(user_id), "is_spam": True}).sort("imported_at", -1)
    messages = []
    for doc in cursor:
        messages.append(format_doc(doc))
    return messages
