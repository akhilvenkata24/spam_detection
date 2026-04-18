import os
import joblib
import re
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from utils.heuristics import parse_heuristics
from utils.url_utils import analyze_urls

# Paths to the saved models
MODELS_DIR = Path(__file__).parent.parent / 'models'
MODEL_PATH = MODELS_DIR / 'spam_ensemble_model.pkl'

# Global variables to hold models in memory
model = None
embedder = None
sentiment_analyzer = None

def load_models():
    """Load the BERT embedder, Sentiment Analyzer, and Classification model."""
    global model, embedder, sentiment_analyzer
    
    # Load SentenceTransformer and VADER
    try:
        print("Loading SentenceTransformer (BERT) array...")
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        sentiment_analyzer = SentimentIntensityAnalyzer()
    except Exception as e:
        print(f"Error loading NLP embedders: {e}")
        
    if MODEL_PATH.exists():
        try:
            model = joblib.load(MODEL_PATH)
            print("Ensemble Model loaded successfully.")
        except Exception as e:
            print(f"Error loading classification model: {e}")
    else:
        print("Warning: Ensemble model file not found. Using fallback prediction.")

def clean_text(text: str) -> str:
    """Clean text (remove URLs) before passing to BERT. BERT handles punctuation fine."""
    text = text.lower()
    # Remove URLs so the semantic understanding isn't confused by random strings
    text = re.sub(r'https?://[^\s]+|www\.[^\s]+', '', text)
    return text.strip()

def predict_spam_probability(raw_text: str) -> float:
    """
    Stage 3: Advanced ML Classifier
    Returns the probability of the message being spam/phishing (0.0 to 1.0)
    using BERT Embeddings and Metadata Arrays.
    """
    if model is None or embedder is None or sentiment_analyzer is None:
        load_models()
        if model is None or embedder is None or sentiment_analyzer is None:
            print("Fallback used as models failed to load (likely OOM).")
            return 0.1 # Fallback
        
    cleaned = clean_text(raw_text)
    if len(cleaned) == 0:
        return 0.0
        
    try:
        # 1. Generate text embeddings (384 dimensions)
        embeddings = embedder.encode([cleaned])
        
        # 2. Extract Metadata Features
        # A. Sentiment/Urgency
        sentiment = sentiment_analyzer.polarity_scores(raw_text)
        neg_score = sentiment['neg']
        
        # B. Heuristics
        heur_res = parse_heuristics(raw_text)
        heur_score = heur_res['score'] / 100.0
        
        # C. URLs
        url_res = analyze_urls(raw_text)
        url_count = 1 if url_res['expanded_urls'] else 0
        url_risk = url_res['score'] / 100.0
        
        meta_features = np.array([[neg_score, heur_score, url_count, url_risk]])
        
        # 3. Combine Features (384 + 4 = 388 dimensions)
        X_test = np.hstack((embeddings, meta_features))
        
        # 4. Predict
        prob = model.predict_proba(X_test)[0][1]
        return float(prob)
        
    except Exception as e:
        print(f"Prediction error in advanced pipeline: {e}")
        return 0.1
