import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from utils.heuristics import parse_heuristics
from utils.url_utils import analyze_urls
from utils.ml_predict import load_models, predict_spam_probability
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from utils.auth import create_user, verify_user, get_user_by_id, get_user_by_api_key, save_scan_history, get_user_history, update_user_settings
from utils.sms import save_user_sms, get_user_sms, get_spam_sms
from utils.db import users_collection
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from datetime import timedelta

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "super-secret-jwt-key-change-in-prod")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)

# Enable CORS for configured frontend origins.
# Set CORS_ORIGINS as comma-separated values in production.
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env.strip():
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]

CORS(
    app,
    resources={r"/*": {"origins": cors_origins}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"]
)

# Rate Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Optional: Simple API Key for basic protection (mobile clients, external services)
API_KEY = os.getenv("API_KEY", "your_secret_api_key_here")

# Initialize models
load_models()

def seed_local_demo_user():
    if os.getenv("SEED_DEMO_USER", "true").lower() not in {"1", "true", "yes"}:
        return

    if users_collection.count_documents({}) > 0:
        return

    demo_username = os.getenv("DEMO_USERNAME", "demo_user")
    demo_email = os.getenv("DEMO_EMAIL", "demo_user@test.local")
    demo_password = os.getenv("DEMO_PASSWORD", "Demo@123")

    user, error = create_user(demo_username, demo_email, demo_password)
    if user and not error:
        logger.info("Seeded local demo user: %s", demo_username)


seed_local_demo_user()

@app.route('/health', methods=['GET'])
@limiter.exempt
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.json
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    user, error = create_user(data['username'], data['email'], data['password'])
    if error:
        return jsonify({"status": "error", "message": error}), 400
        
    return jsonify({"status": "success", "message": "User registered successfully"}), 201

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("30 per minute")
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    user = verify_user(data['username'], data['password'])
    if not user:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        
    access_token = create_access_token(identity=str(user['_id']))
    return jsonify({
        "status": "success", 
        "access_token": access_token, 
        "user": {
            "username": user['username'], 
            "api_key": user['api_key'], 
            "settings": user['settings']
        }
    }), 200

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "status": "error",
        "message": "Too many login attempts. Please wait a moment and try again."
    }), 429

@app.route('/api/dashboard/history', methods=['GET'])
@jwt_required()
@limiter.exempt
def get_history():
    user_id = get_jwt_identity()
    history = get_user_history(user_id)
    sms_messages = get_user_sms(user_id)
    
    # Merge and standardize format
    combined = []
    for h in history:
        combined.append(h)
        
    for s in sms_messages:
        combined.append({
            "_id": s["_id"],
            "user_id": s["user_id"],
            "text_snippet": s["body"][:100] + "..." if len(s["body"]) > 100 else s["body"],
            "full_text": s["body"],
            "risk_score": s["risk_score"],
            "verdict": "high_risk" if s["is_spam"] else "safe",
            "source": "Mobile SMS Sync",
            "timestamp": s["imported_at"],
            "sender": s.get("sender", "unknown")
        })
        
    # Sort combined history by timestamp descending
    combined.sort(key=lambda x: str(x.get('timestamp', '')), reverse=True)
    # Limit to top 50 in dashboard
    combined = combined[:50]
    
    return jsonify({"status": "success", "history": combined}), 200

@app.route('/api/dashboard/history/bulk', methods=['DELETE'])
@jwt_required()
@limiter.exempt
def delete_history_bulk():
    try:
        user_id = get_jwt_identity()
        data = request.json
        if not data or 'ids' not in data:
            return jsonify({"status": "error", "message": "Missing ids"}), 400
            
        from utils.db import history_collection, sms_collection
        from bson.objectid import ObjectId
        
        object_ids = [ObjectId(i) for i in data['ids']]
        history_collection.delete_many({"_id": {"$in": object_ids}, "user_id": ObjectId(user_id)})
        sms_collection.delete_many({"_id": {"$in": object_ids}, "user_id": ObjectId(user_id)})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        import traceback
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/dashboard/history/<item_id>', methods=['DELETE'])
@jwt_required()
@limiter.exempt
def delete_history_item(item_id):
    try:
        user_id = get_jwt_identity()
        from utils.db import history_collection, sms_collection
        from bson.objectid import ObjectId
        
        # Check if it exists in history
        res = history_collection.delete_one({"_id": ObjectId(item_id), "user_id": ObjectId(user_id)})
        if res.deleted_count == 0:
            # Maybe it's an SMS being deleted from history
            res2 = sms_collection.delete_one({"_id": ObjectId(item_id), "user_id": ObjectId(user_id)})
            if res2.deleted_count == 0:
                return jsonify({"status": "error", "message": "Item not found"}), 404
                
        return jsonify({"status": "success", "message": "Deleted successfully"}), 200
    except Exception as e:
        import traceback
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
@limiter.exempt
def get_stats():
    user_id = get_jwt_identity()
    history = get_user_history(user_id, limit=1000) # Get all for stats
    sms_messages = get_user_sms(user_id)
    
    total_scans = len(history) + len(sms_messages)
    threats_blocked = sum(1 for h in history if h['risk_score'] >= 60) + sum(1 for s in sms_messages if s['is_spam'])
    api_calls = sum(1 for h in history if h['source'] == "API (Mobile)")
    
    return jsonify({
        "status": "success", 
        "stats": {
            "total_scans": total_scans,
            "threats_blocked": threats_blocked,
            "api_calls": api_calls
        }
    }), 200

@app.route('/api/dashboard/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    user_id = get_jwt_identity()
    data = request.json
    if not data or 'settings' not in data:
        return jsonify({"status": "error", "message": "Missing settings"}), 400
        
    update_user_settings(user_id, data['settings'])
    return jsonify({"status": "success", "message": "Settings updated"}), 200

@app.route('/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze():
    # 1. API Key Auth check
    # Disabled strictly for CORS dev environment (or you can pass header from frontend)
    # if not verify_api_key(request):
    #     return jsonify({"status": "error", "message": "Unauthorized API Key"}), 401

    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({"status": "error", "message": "Missing 'text' field in request body"}), 400
        
        # Extract text into temporary memory
        raw_text = str(data.get('text', ''))
        sender = data.get('sender', 'unknown')
        source = data.get('source', 'unknown')
        
        # Check authentication optionally to attribute to user
        user_id = None
        user_settings = {"storage_threshold": 60, "auto_flag": False}
        req_source = source

        # Check API Key first (Mobile/External API)
        api_key = request.headers.get("X-API-Key")
        if api_key:
            user = get_user_by_api_key(api_key)
            if user:
                user_id = user['_id']
                user_settings = user['settings']
                req_source = "API (Mobile)"
                
        # If no API Key, try JWT (Web frontend)
        if not user_id:
            try:
                verify_jwt_in_request(optional=True)
                identity = get_jwt_identity()
                if identity:
                    user_id = identity
                    user = get_user_by_id(user_id)
                    if user:
                        user_settings = user['settings']
                    req_source = "Web"
            except Exception:
                pass
        
        # Log request (without raw text)
        logger.info(f"Incoming /analyze request from source: {source}, sender: {sender}")
        
        # --- Stage 1: Heuristic Analysis ---
        heuristic_results = parse_heuristics(raw_text)
        heuristic_score = heuristic_results["score"]
        triggers = heuristic_results["triggers"]
        
        # --- Stage 2: URL Forensics ---
        url_results = analyze_urls(raw_text)
        url_risk = url_results["score"]
        extracted_urls = url_results["expanded_urls"]
        triggers.extend(url_results["triggers"])
        
        # --- Stage 3: ML Classifier ---
        ml_probability = predict_spam_probability(raw_text)
        ml_score_out_of_100 = ml_probability * 100
        
        # --- Risk Aggregator ---
        # User Instruction: generate scores for all three, aggregate, then decide probability
        
        # 1. Base weights
        # Heuristics (0-100) -> 30% of final score
        # ML Prob (0-100) -> 40% of final score
        # URL Risk (0-100) -> 30% of final score
        
        weight_heuristics = 0.30
        weight_ml = 0.40
        weight_url = 0.30
        
        # If no URLs were found, distribute the URL weight to the other two
        if not extracted_urls:
            weight_heuristics = 0.40
            weight_ml = 0.60
            weight_url = 0.0
            
        final_score = (
            (heuristic_score * weight_heuristics) + 
            (ml_score_out_of_100 * weight_ml) + 
            (url_risk * weight_url)
        )
        
        # Automatic High-Risk Overrides (if any single engine is screaming "FRAUD")
        # 1. If heuristics caught 3+ severe classic scams (score >= 80)
        if heuristic_score >= 80:
            final_score = max(final_score, 85)
            
        # 2. If URLs point to incredibly suspicious domains (score == 100)
        if url_risk >= 85:
            final_score = max(final_score, 85)
            
        # 3. If ML is remarkably confident (> 85%)
        if ml_probability > 0.85:
            final_score = max(final_score, 90)
            
        # 4. ENFORCE AUTO-FLAG: If user set Auto-Flag to ON and ANY malicious URL risk is detected
        if user_settings.get("auto_flag", False) and url_risk > 0:
            final_score = 100
            triggers.append("SYSTEM OVERRIDE: Auto-Flagged Malicious Link")
            
        final_score_clamped = max(0, min(100, int(round(final_score))))
        
        # Assign Verdict based on new aggregated score
        if final_score_clamped < 40:
            verdict = "safe"
            reason = "Message looks normal. No obvious threat indicators."
        elif final_score_clamped < 70:
            verdict = "suspicious"
            reason = "Contains some risk indicators. Proceed with caution."
        elif final_score_clamped < 85:
            verdict = "high_risk"
            reason = "High likelihood of spam. Do not click links."
        else:
            verdict = "fraud"
            reason = "Severe threat detected. This is a known scam pattern."
            
        response = {
            "status": "success",
            "risk_score": final_score_clamped,
            "verdict": verdict,
            "reason": reason,
            "details": {
                "heuristic_score": heuristic_score,
                "url_risk": url_risk if extracted_urls else None,
                "ml_probability": round(ml_probability, 4),
                "found_triggers": triggers,
                "extracted_urls": extracted_urls if extracted_urls else None
            }
        }
        
        # Save to history if an authenticated user
        if user_id:
            save_scan_history(user_id, raw_text, final_score_clamped, verdict, req_source, response["details"])
        
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error occurred."}), 200

    finally:
        # Privacy: wipe temporary variables holding raw user content
        raw_text = None
        data = None

@app.route('/api/upload-sms', methods=['POST'])
@jwt_required()
@limiter.exempt
def upload_sms():
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or 'messages' not in data or not isinstance(data['messages'], list):
        return jsonify({"status": "error", "message": "Invalid payload format. Expected {'messages': [...]}"}), 400
        
    messages_payload = data['messages']
    processed_messages = []
    
    for msg in messages_payload:
        body = msg.get("body", "")
        # Run ML model on each message
        ml_probability = predict_spam_probability(body)
        risk_score = int(round(ml_probability * 100))
        
        # Determine is_spam boolean
        is_spam = True if ml_probability > 0.50 else False
        
        processed_message = {
            "sender": msg.get("sender", "unknown"),
            "body": body,
            "date": msg.get("date", ""),
            "is_spam": is_spam,
            "risk_score": risk_score
        }
        processed_messages.append(processed_message)
        
    # Store to DB linked to user
    save_user_sms(user_id, processed_messages)
    
    return jsonify({
        "status": "success", 
        "message": f"Successfully processed and stored {len(processed_messages)} messages."
    }), 201

@app.route('/api/messages/bulk', methods=['DELETE'])
@jwt_required()
@limiter.exempt
def delete_sms_bulk():
    user_id = get_jwt_identity()
    data = request.json
    if not data or 'ids' not in data:
        return jsonify({"status": "error", "message": "Missing ids"}), 400
        
    from utils.db import sms_collection
    from bson import ObjectId
    try:
        object_ids = [ObjectId(i) for i in data['ids']]
        sms_collection.delete_many({"_id": {"$in": object_ids}, "user_id": ObjectId(user_id)})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/messages/<msg_id>', methods=['DELETE'])
@jwt_required()
@limiter.exempt
def delete_sms(msg_id):
    user_id = get_jwt_identity()
    from utils.db import sms_collection
    from bson import ObjectId
    try:
        res = sms_collection.delete_one({"_id": ObjectId(msg_id), "user_id": ObjectId(user_id)})
        if res.deleted_count == 0:
            return jsonify({"status": "error", "message": "Message not found"}), 404
        return jsonify({"status": "success", "message": "Message deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid ID"}), 400

@app.route('/api/messages', methods=['GET'])
@jwt_required()
@limiter.exempt
def get_messages():
    user_id = get_jwt_identity()
    messages = get_user_sms(user_id)
    return jsonify({"status": "success", "messages": messages}), 200

@app.route('/api/spam', methods=['GET'])
@jwt_required()
def get_spam():
    user_id = get_jwt_identity()
    spam_messages = get_spam_sms(user_id)
    return jsonify({"status": "success", "spam_messages": spam_messages}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
# Trigger Hugging Face sync

