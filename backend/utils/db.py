import os
from pymongo import MongoClient

# Use Railway's MONGO_URL if available, otherwise MONGO_URI, fallback to localhost
MONGO_URI = os.getenv("MONGO_URL", os.getenv("MONGO_URI", "mongodb://localhost:27017"))
DB_NAME = "spam_detection_db"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
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
    sms_collection.create_index("user_id")
    sms_collection.create_index([("date", -1)])
    print("MongoDB indices verified.")
except Exception as e:
    print(f"Warning: MongoDB connection or index creation failed: {e}")
