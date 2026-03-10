import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from utils.heuristics import parse_heuristics
from utils.url_utils import analyze_urls
from utils.ml_predict import load_models, predict_spam_probability

# Setup minimal logging (do not log raw messages)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for React frontend and anything else securely
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://your-frontend-domain.com", "*"]}})

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

def verify_api_key(req):
    """Checks API key in header."""
    key = req.headers.get("X-API-Key")
    # For dev purposes, if API_KEY is set to 'dev_mode', bypass auth.
    if API_KEY != 'dev_mode' and key != API_KEY:
        return False
    return True

@app.route('/health', methods=['GET'])
@limiter.exempt
def health_check():
    return jsonify({"status": "ok"}), 200

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
        # If ML is highly confident (>80%), trust it heavily.
        if ml_probability > 0.8:
            final_score = (0.3 * heuristic_score) + (0.2 * url_risk) + (0.5 * ml_score_out_of_100)
        else:
            final_score = (0.4 * heuristic_score) + (0.3 * url_risk) + (0.3 * ml_score_out_of_100)
            
        final_score_clamped = max(0, min(100, int(round(final_score))))
        
        # Assign Verdict
        if final_score_clamped < 40:
            verdict = "safe"
            reason = "Message looks normal. No obvious threat indicators."
        elif final_score_clamped <= 74:
            verdict = "suspicious"
            reason = "Contains some risk indicators. Proceed with caution."
        else:
            verdict = "high_risk" if heuristic_score < 80 and url_risk < 80 else "fraud"
            reason = "High probability of scam/fraud. Do not click links or share information."
            
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
        
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error occurred."}), 200

    finally:
        # Privacy: wipe temporary variables holding raw user content
        raw_text = None
        data = None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
