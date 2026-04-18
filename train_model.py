import pandas as pd
import numpy as np
import joblib
import os
import sys
from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
from sentence_transformers import SentenceTransformer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from utils.ml_predict import clean_text
from utils.heuristics import parse_heuristics
from utils.url_utils import extract_urls


def fast_training_url_features(text: str):
    """Cheap URL features for offline training without WHOIS/network calls."""
    urls = extract_urls(text)
    if not urls:
        return 0, 0.0

    suspicious_score = 0
    suspicious_tlds = ['.xyz', '.top', '.click', '.loan', '.buzz', '.info', '.tk', '.ml']
    for url in urls:
        parsed = urlparse(url if url.startswith(('http://', 'https://')) else f'http://{url}')
        domain = parsed.netloc.lower()
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            suspicious_score += 1
        if domain.count('-') >= 2:
            suspicious_score += 1
        if any(k in domain for k in ['login', 'verify', 'update', 'secure', 'account', 'bank']):
            suspicious_score += 1

    url_count = 1
    normalized_risk = min(1.0, suspicious_score / max(1, len(urls) * 3))
    return url_count, normalized_risk

def extract_metadata_features(text, sentiment_analyzer):
    # 1. Sentiment & Urgency
    sentiment = sentiment_analyzer.polarity_scores(text)
    neg_score = sentiment['neg'] # High negativity/stress is common in scams
    
    # 2. Heuristics score
    heur_res = parse_heuristics(text)
    heur_score = heur_res['score'] / 100.0 # Normalize 0-1
    
    # 3. URL Count & Risk (fast local-only extraction for training speed)
    url_count, url_risk = fast_training_url_features(text)
    
    return [neg_score, heur_score, url_count, url_risk]

def train_and_save_advanced_model(dataset_path: str, models_dir: str):
    print(f"Loading dataset from {dataset_path}...")
    try:
        df = pd.read_csv(dataset_path)
        # Using phishing_legit_dataset_KD_10000.csv (text, label)
        # label: 1 = phishing, 0 = legit
        df = df[['text', 'label']].dropna()
    except Exception as e:
        print(f"Error reading {dataset_path}: {e}")
        return
        
    print(f"Dataset shape: {df.shape}")
    print(df['label'].value_counts())
    
    # Initialize models for Feature Extraction
    print("Loading SentenceTransformer (BERT) and VADER...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2') 
    sentiment_analyzer = SentimentIntensityAnalyzer()
    
    print("Extracting features (this may take a minute depending on CPU)...")
    texts = df['text'].astype(str).tolist()
    
    # 1. BERT Embeddings (384 dimensions)
    embeddings = embedder.encode(texts, show_progress_bar=True)
    
    # 2. Metadata Features (4 dimensions)
    print("Extracting Metadata (Sentiment, Heuristics, URLs)...")
    meta_features = np.array([extract_metadata_features(t, sentiment_analyzer) for t in texts])
    
    # Combine Embeddings + Metadata
    X = np.hstack((embeddings, meta_features))
    y = df['label'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"\nTraining data shape: {X_train.shape}")
    
    # Evaluate Multiple Algorithms
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
        "GaussianNB": GaussianNB(), # MultinomialNB doesn't support negative values from BERT
        "XGBoost": xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    }
    
    best_model = None
    best_acc = 0
    best_name = ""
    
    print("\n--- Evaluating Algorithms ---")
    for name, clf in models.items():
        print(f"Training {name}...")
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        print(f"{name} Accuracy: {acc:.4f}")
        
        if acc > best_acc:
            best_acc = acc
            best_model = clf
            best_name = name
            
    print(f"\nBest Model: {best_name} ({best_acc:.4f})")
    if best_model is None:
        raise RuntimeError("No valid model was trained; aborting artifact save.")
    print(classification_report(y_test, best_model.predict(X_test), target_names=['Legit', 'Phishing']))
    
    # Save the winning model
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, 'spam_ensemble_model.pkl')
    
    joblib.dump(best_model, model_path)
    print(f"\nSuccessfully saved {best_name} -> {model_path}")
    print("Note: SentenceTransformer is downloaded on the fly by the backend, no need to save it via joblib.")

if __name__ == "__main__":
    train_and_save_advanced_model('phishing_legit_dataset_KD_10000.csv', 'backend/models')
