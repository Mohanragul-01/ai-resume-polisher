## AI Resume Polisher

Upload a **resume** and a **job description** (PDF or DOCX). The app returns:

- **match_score** (0–100)
- **tailored_resume** (rewritten resume text)

This repo has two folders:

- `backend/`: Flask API (`POST /analyze`)
- `frontend/`: React + Vite UI (file upload + results)

### Run locally (development)

**Backend**

```powershell
cd "d:\Projects\1_AI_Resume_Polisher\backend"
.\myenv\Scripts\Activate.ps1
$env:GEMINI_API_KEY="YOUR_KEY"
python -m flask --app app run --host 127.0.0.1 --port 5000
```

**Frontend**

```powershell
cd "d:\Projects\1_AI_Resume_Polisher\frontend"
npm install
npm run dev
```

Open `http://localhost:5173`.

### Deploy (high level)

- **Frontend**: deploy `frontend/` to Vercel
- **Backend**: deploy `backend/` to Render
  - set environment variables (at least `GEMINI_API_KEY`)
  - set `CORS_ORIGINS` to your frontend URL (comma-separated if multiple)

