---
title: Spam Detection Backend
emoji: 🚀
colorFrom: blue
colorTo: red
sdk: docker
app_file: app.py
app_port: 7860
pinned: false
---

## SPAM.DETECT — Advanced Threat & Spam Analysis

**Download the Android APK (Release V1):**  
[![Download APK](https://img.shields.io/badge/Download-APK-brightgreen?style=for-the-badge&logo=android)](https://github.com/akhilvenkata24/spam_detection/releases/download/V1/app-debug.apk)

A full-stack threat analysis platform, along with android app support that detects spam/phishing risk from message **content** using a hybrid engine:
- Rule-based heuristics
- URL forensics
- Machine learning probability scoring

---

## Features
- Content-based spam/phishing analysis (`/analyze`)
- Explainable results: risk score, verdict, trigger flags, reason
- User auth with JWT (register/login)
- API key support for mobile/external ingestion
- Dashboard with:
  - scan history
  - live stats
  - synced SMS inbox
  - settings (threshold + auto-flag)
- MongoDB-backed persistence for users, scans, and SMS data

---

## Tech Stack
### Frontend
- React + Vite
- react-router-dom
- lucide-react
- framer-motion

### Backend
- Flask
- flask-jwt-extended
- flask-cors
- flask-limiter
- flask-bcrypt
- pymongo
- sentence-transformers (all-MiniLM-L6-v2)
- VADER Sentiment
- scikit-learn / xgboost / pandas / numpy / joblib
- requests / whois

### Database
- MongoDB

---

## Project Structure

```text
spam_detection-main/
  README.md
  DOCUMENTATION_SOURCE.md
  spam.csv
  train_model.py
  analyze_spam.py
  update_urls.py

  backend/
    app.py
    requirements.txt
    train_custom_model.py
    test_sms.py
    test_messages.py
    models/
    utils/

  frontend/
    package.json
    src/
      pages/
      components/
      context/
      layouts/
```

---

## Core Detection Workflow
1. User submits text for analysis.
2. Backend runs **Stage 1 Heuristics** (regex + scam patterns).
3. Backend runs **Stage 2 URL Forensics** (extract, expand, domain risk, WHOIS age checks).
4. Backend runs **Stage 3 ML** (BERT embeddings + metadata features).
5. Weighted aggregator computes final score and verdict:
   - `safe`
   - `suspicious`
   - `high_risk`
   - `fraud`

### Aggregation Weights
- Heuristics: 30%
- ML: 40%
- URL: 30%

When no URL exists:
- Heuristics: 40%
- ML: 60%

---

## Android App (APK) — Install Notes
- Download using the button above (Release **V1**).
- Install the APK (you may need to allow **Install unknown apps**).
- The app may request SMS permissions (e.g., `READ_SMS`) to analyze message content for spam/phishing detection.

---

## API Overview
### Public
- `GET /health`
- `POST /analyze`

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`

### Dashboard
- `GET /api/dashboard/history`
- `DELETE /api/dashboard/history/<item_id>`
- `DELETE /api/dashboard/history/bulk`
- `GET /api/dashboard/stats`
- `PUT /api/dashboard/settings`

### SMS
- `POST /api/upload-sms`
- `GET /api/messages`
- `DELETE /api/messages/<msg_id>`
- `DELETE /api/messages/bulk`
- `GET /api/spam`

---

## Datasets & Models
### Datasets
- `spam.csv` (ham/spam SMS dataset, ~5.5k rows)
- Optional external dataset in `train_model.py`: `phishing_legit_dataset_KD_10000.csv`

### Model Artifacts
- `backend/models/spam_ensemble_model.pkl` (active classifier)
- `backend/models/tfidf_vectorizer.pkl` (artifact available)

### Training Pipelines
- `train_model.py`: compares RandomForest, GaussianNB, XGBoost and saves best model.
- `backend/train_custom_model.py`: trains Logistic Regression on embedding + metadata features.

---

## Local Development Setup

## 1) Backend
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend default: `http://localhost:5173`  
Backend default: `http://127.0.0.1:5000`

---

## Environment Variables
### Backend
- `JWT_SECRET`
- `MONGO_URI`
- `API_KEY`
- `CORS_ORIGINS`

### Frontend
- `VITE_API_BASE_URL`

Example frontend env:
```env
VITE_API_BASE_URL=http://127.0.0.1:5000
```

Templates:
- `backend/.env.example`
- `frontend/.env.example`

---

## Deployment
For full deployment steps (Render + MongoDB Atlas), see:
- `DEPLOYMENT.md`

---

## Security Notes
- Passwords hashed with bcrypt
- JWT-based protected endpoints
- Rate limits on sensitive endpoints
- Optional API-key based access for ingestion clients
- CORS enabled (tighten origin list for production)

---

## Testing Utilities
- `backend/test_sms.py`
- `backend/test_messages.py`

---

## Documentation Source
For full formal/academic/project documentation material (architecture, workflows, ML internals, datasets, heuristics, deployment notes), use:
- **`DOCUMENTATION_SOURCE.md`**

---

## Roadmap (Short)
- Finalize production deployment and infra hardening
- Improve model observability and drift tracking
- Expand multilingual detection coverage
- Add CI/CD checks for backend + frontend
