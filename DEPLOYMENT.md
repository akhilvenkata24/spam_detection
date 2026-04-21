# Deployment Guide

This project is easiest to deploy with:
- Frontend: Render Static Site
- Backend: Hugging Face Spaces (Docker)
- Database: MongoDB Atlas

## 1) MongoDB Atlas
1. Create a free/shared cluster in MongoDB Atlas.
2. Create a DB user and password.
3. In Network Access, allow your deployment platform IPs (or use temporary 0.0.0.0/0 for testing).
4. Copy the `mongodb+srv://...` connection string.

## 2) Deploy Backend on Hugging Face Spaces
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces).
2. Choose **Docker** as the Space SDK.
3. Select "Blank" template.
4. Clone your repository into the Space or sync it via GitHub.
5. In the Space settings, add your Secrets (Environment Variables):
   - `JWT_SECRET` (required)
   - `MONGO_URI` (required)
   - `CORS_ORIGINS` (required, set to `*` or your frontend URL)
   - `API_KEY` (optional, for mobile API ingestion)
6. Docker build/run in Space:
   - App file: `backend/app.py`
   - Exposed port: `7860` at the Space proxy level (Flask still runs internal `PORT` env)
7. Use the Space "Restart this Space" / "Factory Rebuild" buttons after each push.
6. Once built, the backend will run at your Hugging Face Space URL.

## 3) Deploy Frontend on Render
1. Create a new Static Site from this repository.
2. Set Root Directory to `frontend`.
3. Build Command: `npm install && npm run build`
4. Publish Directory: `dist`
5. Add env var:
   - `VITE_API_BASE_URL=https://<your-huggingface-space-domain>`
6. Deploy.
7. For updates, use Render "Manual Deploy" -> "Deploy latest commit" (rebuild).

## 4) Set CORS correctly
After frontend deploy, set backend `CORS_ORIGINS` exactly to your frontend origin.
Example:
- `https://spam-detect-frontend.onrender.com`

If you use multiple frontend domains, separate with commas.

## 5) Post-deploy checklist
- Register a new user in production.
- Login and open dashboard.
- Submit scanner input and verify history/stat updates.
- Verify Forgot Password flow from login screen.
- Verify account update + change password from dashboard settings.
- Confirm backend logs show requests from frontend origin.

## 6) Notes
- First backend boot can be slower while model files are loaded/cached.
- Keep `JWT_SECRET` private.
- Prefer MongoDB Atlas over local MongoDB for hosted deployments.
