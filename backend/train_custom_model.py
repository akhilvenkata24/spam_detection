import os
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from train_model import train_and_save_advanced_model


DATASET_PATH = ROOT.parent / "phishing_legit_dataset_KD_10000.csv"
MODELS_DIR = ROOT / "models"
MODEL_PATH = MODELS_DIR / "spam_ensemble_model.pkl"


def ensure_model_artifact_is_valid(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Model artifact not found: {path}")
    if path.stat().st_size < 1024:
        raise ValueError(f"Model artifact too small ({path.stat().st_size} bytes): {path}")

    model = joblib.load(path)
    if not hasattr(model, "predict_proba"):
        raise TypeError("Model artifact does not support predict_proba")


def main() -> None:
    print("[1/3] Training and exporting model artifact...")
    train_and_save_advanced_model(str(DATASET_PATH), str(MODELS_DIR))

    print("[2/3] Validating artifact integrity...")
    ensure_model_artifact_is_valid(MODEL_PATH)
    print(f"Model artifact verified: {MODEL_PATH}")

    print("[3/3] Calibrating verdict thresholds from dataset...")
    from calibrate_thresholds import main as calibrate_main

    calibrate_main()
    print("Retrain + calibration completed successfully.")


if __name__ == "__main__":
    main()
