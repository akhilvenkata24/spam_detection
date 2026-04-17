# Deployment Guide

This project is easiest to deploy with:
- Frontend: Render Static Site
- Backend: Render Web Service (Docker)
- Database: MongoDB Atlas

## 1) MongoDB Atlas
1. Create a free/shared cluster in MongoDB Atlas.
2. Create a DB user and password.
3. In Network Access, allow your deployment platform IPs (or use temporary 0.0.0.0/0 for testing).
4. Copy the `mongodb+srv://...` connection string.

## 2) Deploy Backend on Render
1. Create a new Web Service from this repository.
2. Set Root Directory to `backend`.
3. Choose Docker deploy (Render auto-detects `backend/Dockerfile`).
4. Add environment variables:
   - `JWT_SECRET` (required)
   - `MONGO_URI` (required)
   - `API_KEY` (optional)
   - `CORS_ORIGINS` (required, set to your frontend URL)
   - `SEED_DEMO_USER=false` (recommended for production)
5. Deploy and verify:
   - `GET https://<your-backend-domain>/health` should return `{ "status": "ok" }`.

## 3) Deploy Frontend on Render
1. Create a new Static Site from this repository.
2. Set Root Directory to `frontend`.
3. Build Command: `npm install && npm run build`
4. Publish Directory: `dist`
5. Add env var:
   - `VITE_API_BASE_URL=https://<your-backend-domain>`
6. Deploy.

## 4) Set CORS correctly
After frontend deploy, set backend `CORS_ORIGINS` exactly to your frontend origin.
Example:
- `https://spam-detect-frontend.onrender.com`

If you use multiple frontend domains, separate with commas.

## 5) Post-deploy checklist
- Register a new user in production.
- Login and open dashboard.
- Submit scanner input and verify history/stat updates.
- Confirm backend logs show requests from frontend origin.

## 6) Notes
- First backend boot can be slower while model files are loaded/cached.
- Keep `JWT_SECRET` private.
- Prefer MongoDB Atlas over local MongoDB for hosted deployments.
