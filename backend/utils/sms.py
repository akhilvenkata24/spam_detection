from datetime import datetime
from bson import ObjectId
from utils.db import sms_collection

def save_user_sms(user_id, messages_list):
    if not messages_list:
        return []

    docs = []
    user_obj_id = ObjectId(user_id) if user_id else None
    or_conditions = []
    
    for msg in messages_list:
        sender = msg.get("sender", "unknown")
        body = msg.get("body", "")
        msg_date = msg.get("date", datetime.utcnow().isoformat() + "Z")

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
            "imported_at": datetime.utcnow().isoformat() + "Z"
        }
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
    
    # Ensure imported_at is string and has Z timezone
    imp = doc.get("imported_at")
    if isinstance(imp, datetime):
        doc["imported_at"] = imp.isoformat() + "Z"
    elif isinstance(imp, str) and not imp.endswith("Z"):
        doc["imported_at"] = imp + "Z"
        
    return doc

def get_user_sms(user_id):
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
