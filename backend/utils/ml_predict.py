import os
import joblib
import re
from pathlib import Path

# Paths to the saved models
MODELS_DIR = Path(__file__).parent.parent / 'models'
VECTORIZER_PATH = MODELS_DIR / 'tfidf_vectorizer.pkl'
MODEL_PATH = MODELS_DIR / 'spam_ensemble_model.pkl'

# Global variables to hold models in memory
vectorizer = None
model = None

def load_models():
    """Load the TF-IDF vectorizer and the classification model."""
    global vectorizer, model
    
    # In a real scenario, you train and save the models using joblib.
    # Instruction to Train/Save Models:
    # 1. Collect dataset (e.g. SMS Spam Collection, Fraudulent Emails).
    # 2. Train a vectorizer:
    #    from sklearn.feature_extraction.text import TfidfVectorizer
    #    tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
    #    X_train_vectorized = tfidf.fit_transform(X_train)
    #    joblib.dump(tfidf, 'models/tfidf_vectorizer.pkl')
    # 3. Train a model:
    #    from sklearn.ensemble import RandomForestClassifier
    #    clf = RandomForestClassifier(n_estimators=100)
    #    clf.fit(X_train_vectorized, y_train)
    #    joblib.dump(clf, 'models/spam_ensemble_model.pkl')
    
    if VECTORIZER_PATH.exists() and MODEL_PATH.exists():
        try:
            vectorizer = joblib.load(VECTORIZER_PATH)
            model = joblib.load(MODEL_PATH)
            print("Models loaded successfully.")
        except Exception as e:
            print(f"Error loading models: {e}")
    else:
        print("Warning: Model files not found. Using fallback prediction.")

def clean_text(text: str) -> str:
    """Clean text before passing to the vectorizer."""
    text = text.lower()
    # Remove URLs
    text = re.sub(r'https?://[^\s]+|www\.[^\s]+', '', text)
    # Remove punctuation and numbers
    text = re.sub(r'[^a-z\s]', '', text)
    # Stop words are optionally handled by the TF-IDF vectorizer or manually here.
    return text.strip()

def predict_spam_probability(text: str) -> float:
    """
    Stage 3: ML Classifier
    Returns the probability of the message being spam (0.0 to 1.0).
    """
    cleaned = clean_text(text)
    
    if vectorizer is not None and model is not None:
        try:
            # Transform text
            tfidf = vectorizer.transform([cleaned])
            # Predict probability (spam class probability is at index 1)
            prob = model.predict_proba(tfidf)[0][1]
            return float(prob)
        except Exception as e:
            print(f"Prediction error: {e}")
            
    # Fallback to a basic ML proxy logic if models are not present
    # This prevents the API from completely failing during initial dev.
    fallback_prob = 0.1
    if len(cleaned) == 0:
        return 0.0
    return min(1.0, fallback_prob)
