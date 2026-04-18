import json
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics import f1_score
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from utils.heuristics import parse_heuristics
from utils.url_utils import extract_urls
from utils.ml_predict import clean_text
import joblib


ROOT = Path(__file__).resolve().parent
DATASET_PATH = ROOT.parent / "phishing_legit_dataset_KD_10000.csv"
MODEL_PATH = ROOT / "models" / "spam_ensemble_model.pkl"
THRESHOLD_PATH = ROOT / "models" / "score_thresholds.json"


def map_target_bucket(label: int, severity: str) -> int:
    """
    Map dataset rows to 4 runtime verdict buckets.
    0=safe, 1=suspicious, 2=high_risk, 3=fraud
    """
    if int(label) == 0:
        return 0

    sev = str(severity).strip().lower()
    if sev == "low":
        return 1
    if sev == "medium":
        return 2
    return 3


def fast_url_features(text: str) -> tuple[int, float]:
    """Cheap URL features for offline calibration without WHOIS/network calls."""
    urls = extract_urls(text)
    if not urls:
        return 0, 0.0

    suspicious = 0
    for url in urls:
        lower = url.lower()
        if any(k in lower for k in ["bit.ly", "tinyurl", "t.ly", "is.gd", "goo.gl", "ow.ly"]):
            suspicious += 1
        if any(k in lower for k in ["login", "verify", "update", "secure", "account", "bank"]):
            suspicious += 1

    # Keep this aligned to model metadata scale (0-1 range).
    risk = min(1.0, suspicious / max(1, len(urls) * 2))
    return 1, risk


def build_feature_matrix(texts: list[str]) -> np.ndarray:
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    sentiment = SentimentIntensityAnalyzer()

    cleaned = [clean_text(str(t)) for t in texts]
    embeddings = embedder.encode(cleaned, show_progress_bar=True)

    metadata_rows = []
    for raw in texts:
        raw_text = str(raw)
        neg_score = sentiment.polarity_scores(raw_text)["neg"]
        heur_score = parse_heuristics(raw_text)["score"] / 100.0
        url_count, url_risk = fast_url_features(raw_text)
        metadata_rows.append([neg_score, heur_score, url_count, url_risk])

    return np.hstack((embeddings, np.array(metadata_rows)))


def labels_from_thresholds(scores: np.ndarray, t1: float, t2: float, t3: float) -> np.ndarray:
    # 0=safe, 1=suspicious, 2=high_risk, 3=fraud
    out = np.zeros(scores.shape[0], dtype=int)
    out[scores >= t1] = 1
    out[scores >= t2] = 2
    out[scores >= t3] = 3
    return out


def optimize_thresholds(probabilities: np.ndarray, targets: np.ndarray) -> tuple[float, float, float, float]:
    # Candidate ranges are quantile-based for stable search on any dataset skew.
    q = np.quantile(probabilities, np.linspace(0.05, 0.98, 32))
    candidates = sorted(set(float(v) for v in q))

    best_f1 = -1.0
    best = (0.40, 0.70, 0.85)

    for t1 in candidates:
        for t2 in candidates:
            if t2 <= t1 + 0.03:
                continue
            for t3 in candidates:
                if t3 <= t2 + 0.03:
                    continue
                pred = labels_from_thresholds(probabilities, t1, t2, t3)
                score = f1_score(targets, pred, average="macro")
                if score > best_f1:
                    best_f1 = score
                    best = (t1, t2, t3)

    return best[0], best[1], best[2], best_f1


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    df = pd.read_csv(DATASET_PATH)
    required = {"text", "label", "severity"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    texts = df["text"].astype(str).tolist()
    targets = np.array([
        map_target_bucket(int(lbl), sev) for lbl, sev in zip(df["label"], df["severity"])
    ])

    X = build_feature_matrix(texts)
    model = joblib.load(MODEL_PATH)
    if not hasattr(model, "predict_proba"):
        raise TypeError("Loaded model does not expose predict_proba; cannot calibrate thresholds")

    probs = model.predict_proba(X)[:, 1]
    t1, t2, t3, macro_f1 = optimize_thresholds(probs, targets)

    payload = {
        "version": 1,
        "source_dataset": str(DATASET_PATH.name),
        "safe_max": int(round(t1 * 100)),
        "suspicious_max": int(round(t2 * 100)),
        "high_risk_max": int(round(t3 * 100)),
        "calibration_macro_f1": round(float(macro_f1), 4),
        "notes": "Thresholds derived from label+severity to align runtime verdict bands.",
    }

    THRESHOLD_PATH.parent.mkdir(parents=True, exist_ok=True)
    THRESHOLD_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved calibrated thresholds to: {THRESHOLD_PATH}")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
