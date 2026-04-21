import os
import logging
import json
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from utils.heuristics import parse_heuristics
from utils.url_utils import analyze_urls
from utils.ml_predict import load_models, predict_spam_probability
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from utils.auth import (
    create_user,
    verify_user,
    get_user_by_id,
    get_user_by_api_key,
    save_scan_history,
    get_user_history,
    update_user_settings,
    update_user_profile,
    change_user_password,
    verify_user_password,
)
from utils.sms import save_user_sms, get_user_sms, get_spam_sms
from utils.db import users_collection
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from datetime import timedelta

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "super-secret-jwt-key-change-in-prod")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)

# Enable CORS for browser clients.
# The app uses JWTs in local/session storage rather than cookies, so the login
# flow does not need a restricted origin list to stay secure.
cors_origins = "*"

CORS(
    app,
    resources={r"/*": {"origins": cors_origins}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    supports_credentials=False,
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

# Models will be lazy-loaded in the analyze route
# to prevent memory-induced startup crashes on small instances.

def seed_local_demo_user():
    if os.getenv("SEED_DEMO_USER", "true").lower() not in {"1", "true", "yes"}:
        return

    try:
        if users_collection.count_documents({}) > 0:
            return
    except Exception as exc:
        logger.warning("Skipping demo user seeding because MongoDB is unavailable: %s", exc)
        return

    demo_username = os.getenv("DEMO_USERNAME", "demo_user")
    demo_email = os.getenv("DEMO_EMAIL", "demo_user@test.local")
    demo_password = os.getenv("DEMO_PASSWORD", "Demo@123")

    user, error = create_user(demo_username, demo_email, demo_password)
    if user and not error:
        logger.info("Seeded local demo user: %s", demo_username)


seed_local_demo_user()


DEFAULT_SCORE_THRESHOLDS = {
    "safe_max": 40,
    "suspicious_max": 70,
    "high_risk_max": 85,
}


def load_score_thresholds() -> dict:
    config_path = Path(__file__).resolve().parent / "models" / "score_thresholds.json"
    if not config_path.exists():
        return DEFAULT_SCORE_THRESHOLDS.copy()

    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        safe_max = int(payload.get("safe_max", DEFAULT_SCORE_THRESHOLDS["safe_max"]))
        suspicious_max = int(payload.get("suspicious_max", DEFAULT_SCORE_THRESHOLDS["suspicious_max"]))
        high_risk_max = int(payload.get("high_risk_max", DEFAULT_SCORE_THRESHOLDS["high_risk_max"]))

        if not (0 < safe_max < suspicious_max < high_risk_max <= 100):
            logger.warning("Invalid calibrated thresholds in %s. Falling back to defaults.", config_path)
            return DEFAULT_SCORE_THRESHOLDS.copy()

        return {
            "safe_max": safe_max,
            "suspicious_max": suspicious_max,
            "high_risk_max": high_risk_max,
        }
    except Exception as exc:
        logger.warning("Failed to load score thresholds: %s", exc)
        return DEFAULT_SCORE_THRESHOLDS.copy()


SCORE_THRESHOLDS = load_score_thresholds()


def get_storage_threshold(user_settings):
    try:
        threshold = int((user_settings or {}).get("storage_threshold", 60))
    except (TypeError, ValueError):
        threshold = 60
    return max(0, min(100, threshold))


def normalize_requested_source(value):
    if not isinstance(value, str):
        return None

    normalized = value.strip()
    if not normalized:
        return None

    # Accept common mobile/client variants and map them to canonical labels.
    compact = "".join(ch for ch in normalized.lower() if ch.isalnum())
    alias_map = {
        "web": "Web",
        "browser": "Web",
        "apimobile": "API (Mobile)",
        "api": "API (Mobile)",
        "mobile": "API (Mobile)",
        "mobilemanualscan": "Mobile Manual Scan",
        "manualscan": "Mobile Manual Scan",
        "manual": "Mobile Manual Scan",
        "mobilesmssync": "Mobile SMS Sync",
        "smssync": "Mobile SMS Sync",
        "sync": "Mobile SMS Sync",
    }
    if compact in alias_map:
        return alias_map[compact]

    allowed_sources = {
        "Web": "Web",
        "API (Mobile)": "API (Mobile)",
        "Mobile Manual Scan": "Mobile Manual Scan",
        "Mobile SMS Sync": "Mobile SMS Sync",
    }
    return allowed_sources.get(normalized)

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
            "email": user.get('email', ''),
            "api_key": user['api_key'], 
            "settings": user['settings']
        }
    }), 200


@app.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
@limiter.exempt
def update_profile():
    user_id = get_jwt_identity()
    data = request.json or {}

    current_password = data.get('current_password')
    ok, error = verify_user_password(user_id, current_password)
    if not ok:
        return jsonify({"status": "error", "message": error}), 400

    username = data.get('username')
    email = data.get('email')
    user, error = update_user_profile(user_id, username=username, email=email)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    return jsonify({
        "status": "success",
        "message": "Profile updated",
        "user": {
            "username": user['username'],
            "email": user.get('email', ''),
            "api_key": user['api_key'],
            "settings": user.get('settings', {})
        }
    }), 200


@app.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def change_password():
    user_id = get_jwt_identity()
    data = request.json or {}
    ok, error = change_user_password(
        user_id,
        data.get('current_password'),
        data.get('new_password'),
    )
    if not ok:
        return jsonify({"status": "error", "message": error}), 400
    return jsonify({"status": "success", "message": "Password changed successfully"}), 200


@app.route('/api/auth/forgot-password', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password():
    return jsonify({
        "status": "coming_soon",
        "message": "Password recovery is not available yet."
    }), 501

@app.errorhandler(429)
def ratelimit_handler(e):
    if request.path == '/analyze':
        message = "Too many analysis requests. Please wait a few seconds and try again."
    elif request.path == '/api/auth/login':
        message = "Too many login attempts. Please wait a moment and try again."
    else:
        message = "Too many requests. Please wait a moment and try again."

    return jsonify({
        "status": "error",
        "message": message
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
            "verdict": s.get("verdict", "suspicious"),
            "source": s.get("source", "Mobile SMS Sync"),
            "timestamp": s["imported_at"],
            "retention_expires_at": s.get("retention_expires_at"),
            "sender": s.get("sender", "unknown")
        })
        
    # Sort combined history by timestamp descending (newest first)
    from datetime import datetime
    def get_sort_key(item):
        ts = item.get('timestamp')
        if isinstance(ts, str):
            try:
                # Parse ISO string
                return datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()
            except:
                return 0
        elif isinstance(ts, datetime):
            return ts.timestamp()
        return 0
    
    combined.sort(key=get_sort_key, reverse=True)
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
    api_calls = sum(1 for h in history if h.get('source') in {"API (Mobile)", "Mobile Manual Scan"})
    
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
        data = request.get_json(silent=True)
        if not data or 'text' not in data:
            return jsonify({"status": "error", "message": "Missing or invalid JSON body. Expected {'text': '...'}"}), 400
        
        # Extract text into temporary memory
        raw_text = str(data.get('text', ''))
        sender = data.get('sender', 'unknown')
        requested_source_raw = data.get('requested_source', data.get('source'))
        requested_source = normalize_requested_source(requested_source_raw)
        source = data.get('source', 'unknown')
        
        # Check authentication optionally to attribute to user
        user_id = None
        user_settings = {"storage_threshold": 60, "auto_flag": False}
        auth_channel = "ANON"
        resolved_source = requested_source

        # Check API Key first (Mobile/External API)
        api_key = request.headers.get("X-API-Key")
        if api_key:
            user = get_user_by_api_key(api_key)
            if user:
                user_id = user['_id']
                user_settings = user['settings']
                auth_channel = "API_KEY"
                if not resolved_source:
                    resolved_source = "API (Mobile)"
                
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
                    auth_channel = "JWT"
                    if not resolved_source:
                        resolved_source = "Web"
            except Exception:
                pass

        if not resolved_source:
            resolved_source = "Web" if auth_channel == "JWT" else "API (Mobile)" if auth_channel == "API_KEY" else "Web"
        
        # Log request (without raw text)
        logger.info(
            "Incoming /analyze request attribution requested_source=%s resolved_source=%s auth_channel=%s sender=%s",
            requested_source_raw,
            resolved_source,
            auth_channel,
            sender,
        )
        
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
        ml_probability = predict_spam_probability(raw_text, heur_res=heuristic_results, url_res=url_results)
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

        # 5. Trigger-aware floor rules (especially for no-link social-engineering spam)
        trigger_set = {str(t).lower() for t in triggers}
        has_financial_lure = any("financial lure" in t for t in trigger_set)
        has_credential_request = any("credential" in t or "banking detail" in t for t in trigger_set)
        has_account_threat = any("account lock" in t or "account takeover" in t for t in trigger_set)

        # A message that triggers core scam indicators should not remain in SAFE only
        # because the ML probability is low.
        if not extracted_urls:
            if any("urgency" in t for t in trigger_set):
                final_score = max(final_score, 30)
            if has_financial_lure:
                final_score = max(final_score, 40)
            if has_credential_request:
                final_score = max(final_score, 65)
            if has_account_threat and has_credential_request:
                final_score = max(final_score, 80)
            if len(trigger_set) >= 2:
                final_score = max(final_score, 55)
            
        final_score_clamped = max(0, min(100, int(round(final_score))))
        
        # Assign Verdict based on new aggregated score
        if final_score_clamped < SCORE_THRESHOLDS["safe_max"]:
            verdict = "safe"
            reason = "Message looks normal. No obvious threat indicators."
        elif final_score_clamped < SCORE_THRESHOLDS["suspicious_max"]:
            verdict = "suspicious"
            reason = "Contains some risk indicators. Proceed with caution."
        elif final_score_clamped < SCORE_THRESHOLDS["high_risk_max"]:
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
        
        # Save authenticated scans; threshold determines whether they expire.
        if user_id:
            save_scan_history(
                user_id,
                raw_text,
                final_score_clamped,
                verdict,
                resolved_source,
                response["details"],
                storage_threshold=get_storage_threshold(user_settings),
                auth_channel=auth_channel,
            )
        
        return jsonify(response), 200

    except Exception as e:
        import traceback
        logger.error(f"Error during analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"status": "error", "message": "Internal server error occurred."}), 500

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
    storage_threshold = 60

    user = get_user_by_id(user_id)
    if user and user.get('settings'):
        storage_threshold = get_storage_threshold(user['settings'])
    
    for msg in messages_payload:
        body = msg.get("body", "")
        # Run ML model on each message
        ml_probability = predict_spam_probability(body)
        risk_score = int(round(ml_probability * 100))

        if risk_score <= 20:
            verdict = "safe"
        elif risk_score <= 50:
            verdict = "suspicious"
        elif risk_score <= 80:
            verdict = "high_risk"
        else:
            verdict = "fraud"
        
        # Determine is_spam boolean
        is_spam = True if ml_probability > 0.50 else False
        
        processed_message = {
            "sender": msg.get("sender", "unknown"),
            "body": body,
            "date": msg.get("date", ""),
            "is_spam": is_spam,
            "risk_score": risk_score,
            "verdict": verdict,
            "source": "Mobile SMS Sync"
        }
        processed_messages.append(processed_message)
        
    # Store all imported SMS; threshold determines permanence vs 3-day retention.
    save_user_sms(user_id, processed_messages, storage_threshold=storage_threshold)
    
    return jsonify({
        "status": "success", 
        "message": f"Successfully processed {len(processed_messages)} messages. Messages at or above the threshold are permanent; lower-risk messages expire in 3 days."
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

