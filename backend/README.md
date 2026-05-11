## Backend (Flask)

### What it does

Provides a single endpoint:

- `POST /analyze`
  - multipart form fields:
    - `resume`: PDF or DOCX
    - `job`: PDF or DOCX
  - response JSON:
    - `match_score` (0–100)
    - `tailored_resume` (string)

### Run locally

```powershell
cd "d:\Projects\1_AI_Resume_Polisher\backend"
.\myenv\Scripts\Activate.ps1
$env:GEMINI_API_KEY="YOUR_KEY"
python -m flask --app app run --host 127.0.0.1 --port 5000
```

### Environment variables

- `GEMINI_API_KEY`: required
- `CORS_ORIGINS`: optional
  - example: `http://localhost:5173,http://127.0.0.1:5173`
  - in production set it to your Vercel domain

### Production start (Render/Linux)

```bash
gunicorn app:app
```

