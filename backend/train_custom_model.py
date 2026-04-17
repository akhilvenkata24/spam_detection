import os
import sys
import pandas as pd
import numpy as np
import joblib
import time

# Ensure we can correctly import from the sibling utility paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentence_transformers import SentenceTransformer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils.heuristics import parse_heuristics
import re
from urllib.parse import urlparse
from utils.ml_predict import clean_text
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


CSV_PATH = r"c:\Users\akhil\Documents\Desktop\Spam_detection (2)\Spam_detection\spam.csv"
MODEL_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "spam_ensemble_model.pkl")

# Offline URL Analyzer for Rapid Training Mode
def offline_analyze_urls(text: str):
    urls = re.findall(r'(https?://[^\s]+|www\.[^\s]+)', text)
    if not urls:
        return {"expanded_urls": None, "score": 0}
    
    max_risk = 0
    suspicious_tlds = ['.xyz', '.top', '.click', '.loan', '.buzz', '.info']
    for url in urls:
        domain = urlparse(url if url.startswith('http') else 'http://'+url).netloc
        score = 0
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain): score += 80
        if any(domain.endswith(t) for t in suspicious_tlds): score += 40
        if domain.count('-') >= 2: score += 20
        max_risk = max(max_risk, min(100, score))
    return {"expanded_urls": urls, "score": max_risk}

def get_features_for_texts(texts):
    print("--- [1/2] Loading AI Embedders and Semantic Analyzers ---")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    sentiment_analyzer = SentimentIntensityAnalyzer()
    
    print(f"Generating 388-dimensional feature arrays for {len(texts)} samples (Please wait)...")
    
    # 1. Clean texts (remove URLs from textual corpus)
    cleaned_texts = [clean_text(str(t)) for t in texts]
    
    # 2. Extract Subword Embeddings
    print("Encoding Deep BERT Vectors...")
    embeddings = embedder.encode(cleaned_texts, show_progress_bar=False)
    
    # 3. Extract Cyber-security Metadata
    print("Extracting Synthetic Metadata Hooks (Heuristics, Links, Sentiment)...")
    meta_features = []
    
    for i, t in enumerate(texts):
        raw_t = str(t)
        
        # A. Semantic Urgency Filter
        neg_score = sentiment_analyzer.polarity_scores(raw_t)['neg']
        
        # B. Fraud Heuristic Keyword Dictionary
        heur_res = parse_heuristics(raw_t)
        heur_score = heur_res['score'] / 100.0
        
        # C. Malicious URL Threat Engines (Offline Bypass mode)
        url_res = offline_analyze_urls(raw_t)
        url_count = 1 if url_res['expanded_urls'] else 0
        url_risk = url_res['score'] / 100.0
        
        meta_features.append([neg_score, heur_score, url_count, url_risk])
        if (i+1) % 1000 == 0:
            print(f"> Processed metadata for {i+1} inputs...")
            
    meta_features = np.array(meta_features)
    
    # Dynamically concatenate BERT and Metadata (384 + 4)
    X = np.hstack((embeddings, meta_features))
    return X


def main():
    print(f"Verifying dataset location...")
    if not os.path.exists(CSV_PATH):
        print(f"FATAL: Custom CSV dataset not found at expected path: {CSV_PATH}")
        sys.exit(1)
        
    print("-- Initialization Sequence Commenced --")
    df = pd.read_csv(CSV_PATH, encoding='latin-1')
    
    # Strict dataset cleaning & label mapping for Kaggle formatted v1/v2 schema
    df = df[['v1', 'v2']].dropna()
    df.columns = ['label', 'message']
    print(f"Dataset imported securely. Detected {df.shape[0]} valid rows.")
    
    # Normalize supervised classifications to int mapping (0=Safe, 1=Fraud)
    df['label'] = df['label'].map({'ham': 0, 'spam': 1})
    
    texts = df['message'].values
    labels = df['label'].values
    
    start_time = time.time()
    
    # Feed corpus to Feature Extraction Engine
    X_features = get_features_for_texts(texts)
    
    print(f"--- [2/2] Training Optimization Sequence ---")
    print(f"Final Data Structure Shape: {X_features.shape}")
    print(f"Extraction Pipeline completed in {time.time() - start_time:.2f} seconds.")
    
    # Scaffold Training Ensembles
    X_train, X_test, y_train, y_test = train_test_split(X_features, labels, test_size=0.15, random_state=42)
    
    print("Initiating scikit-learn advanced Logistic Regression (Class-Weighted)...")
    clf = LogisticRegression(max_iter=1500, class_weight='balanced')
    clf.fit(X_train, y_train)
    
    # Evaluator Metrics Output
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred) * 100
    print("\n--- Target Model Analysis ---")
    print(f"Accuracy Metric Check: {acc:.2f}%")
    print(classification_report(y_test, y_pred))
    
    # Safely overwrite backend brain
    print("Commencing live override of active ML weights...")
    os.makedirs(os.path.dirname(MODEL_OUTPUT), exist_ok=True)
    joblib.dump(clf, MODEL_OUTPUT)
    print(f"SUCCESS: System Architecture Overridden. AI brain hot-swapped at: {MODEL_OUTPUT}")

if __name__ == "__main__":
    main()
