# Deployment Guide — Smart Resume Screener

This guide covers the most straightforward ways to deploy the **Smart Resume Screener** to production.

---

## Option 1: 1-Click Deploy on Render (Recommended - Free / Low Cost)

Render can build the React frontend and run the FastAPI backend in a single unified web service.

### Steps:
1. **Push your repository to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare deployment configuration"
   git push origin main
   ```
2. Go to [**dashboard.render.com**](https://dashboard.render.com/) and click **New +** → **Web Service**.
3. Connect your GitHub repository.
4. Fill in the settings:
   - **Name**: `smart-resume-screener`
   - **Language / Environment**: `Python 3`
   - **Region**: Select closest to you (e.g. `Frankfurt`, `Oregon`, `Singapore`)
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
5. **Environment Variables**:
   - `PYTHON_VERSION`: `3.12.0`
   - `NODE_VERSION`: `20.9.0`
   - `LLM_PROVIDER`: `mock` *(or `openai` / `gemini` if using API keys)*
   - `LLM_API_KEY`: *(optional: your OpenAI / Gemini API key)*
6. Click **Create Web Service**. Render will build the UI and start the server. Your live app will be accessible at `https://<your-service-name>.onrender.com`.

---

## Option 2: Deploy with Docker / Docker Compose

If you have a VPS (DigitalOcean, AWS EC2, Linode, Hetzner) or local Docker:

### 1. Build and Run Container:
```bash
docker compose up --build -d
```

### 2. Verify:
Open your browser and navigate to:
```
http://localhost:8000
```
*(or `http://<your-server-ip>:8000`)*

---

## Option 3: Deploy on Railway

1. Go to [**railway.app**](https://railway.app/) and create a new project.
2. Select **Deploy from GitHub repo**.
3. In service settings, Railway will automatically detect the root `Dockerfile` and build both the frontend and backend in a unified container.
4. Under **Variables**, add:
   - `PORT`: `8000`
5. Generate a public domain under **Networking** → **Generate Domain**.

---

## Option 4: Split Deployment (Frontend on Vercel + Backend on Render)

If you prefer hosting the static frontend on Vercel:

### 1. Backend (on Render/Railway/Fly.io):
- Deploy `backend/` as a Python web service.
- Note your live backend URL (e.g. `https://smart-resume-api.onrender.com`).

### 2. Frontend (on Vercel):
- Connect your GitHub repo to [**vercel.com**](https://vercel.com).
- Set **Root Directory** to `frontend`.
- Add Environment Variable:
  - `VITE_API_BASE_URL`: `https://smart-resume-api.onrender.com/api`
- Deploy!

---

## Health Check & Verification

Once deployed, you can verify your service status anytime at:
- **Web UI**: `https://<your-domain>/`
- **Health Check**: `https://<your-domain>/api/health`
- **Swagger Documentation**: `https://<your-domain>/docs`
