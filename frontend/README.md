## Frontend (React + Vite + Tailwind)

### Run locally

```powershell
cd "d:\Projects\1_AI_Resume_Polisher\frontend"
npm install
npm run dev
```

Open `http://localhost:5173`.

### Configure backend URL

By default the frontend calls:

- `http://127.0.0.1:5000/analyze`

To change it, create a `.env.local` file in `frontend/`:

```bash
VITE_API_BASE_URL=https://your-backend.example.com
```

Then restart `npm run dev`.
