import pandas as pd
import joblib
import os
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from utils.ml_predict import clean_text

def train_and_save_model(dataset_path: str, models_dir: str):
    print(f"Loading dataset from {dataset_path}...")
    try:
        df = pd.read_csv(dataset_path, encoding='latin-1')
    except Exception as e:
        print(f"Error reading {dataset_path}: {e}")
        return

    # Assuming standard SMS Spam Collection format: v1 (label: ham/spam), v2 (text message)
    df = df.iloc[:, :2]
    df.columns = ['label', 'text']
    
    # Drop rows with missing text
    df = df.dropna(subset=['text'])
    
    print(f"Dataset shape: {df.shape}")
    print(df['label'].value_counts())
    
    # Clean text using the exact same function the backend uses
    print("Cleaning text data...")
    df['cleaned_text'] = df['text'].apply(str).apply(clean_text)
    
    # Map labels to binary: ham=0, spam=1
    df['is_spam'] = df['label'].map({'spam': 1, 'ham': 0}).fillna(0).astype(int)
    
    X = df['cleaned_text']
    y = df['is_spam']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("Training Random Forest Classifier (n_estimators=100)...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    clf.fit(X_train_vec, y_train)
    
    print("\n--- Evaluate on Test Set ---")
    y_pred = clf.predict(X_test_vec)
    print(classification_report(y_test, y_pred, target_names=['Ham', 'Spam']))
    
    # Save models
    os.makedirs(models_dir, exist_ok=True)
    vec_path = os.path.join(models_dir, 'tfidf_vectorizer.pkl')
    model_path = os.path.join(models_dir, 'spam_ensemble_model.pkl')
    
    joblib.dump(vectorizer, vec_path)
    joblib.dump(clf, model_path)
    
    print(f"\nSuccessfully saved components:")
    print(f"Vectorizer -> {vec_path}")
    print(f"Model -> {model_path}")
    
    print("NOTE: You must restart the Flask backend to load these new models!")

if __name__ == "__main__":
    train_and_save_model('spam.csv', 'backend/models')
