# Claude Skills Web Hub

Web front-end for the six Helio Claude Skills (GWA autofill, GWA Level 1 report,
Helio Pre-Dev report, Helio feasibility tiers, HTML card populator, Land Use
prompt builder). FastAPI backend + React (Vite) frontend, dark glassmorphism UI.

## Setup

### Backend
```bash
cd backend
python -m venv .venv
.venv/Scripts/activate       # Windows
pip install -r requirements.txt
cp .env.example .env         # then set ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

`SKILLS_ROOT` defaults to the bundled `skills/` folder at the project root
(each skill's `SKILL.md` lives at `skills/<skill-name>/<skill-name>/SKILL.md`).
Only set `SKILLS_ROOT` in `.env` if you want to point at a different location.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173. The Vite dev server proxies `/api/*` to
`http://127.0.0.1:8000`.

## What's deterministic vs. LLM-assisted

- **Deterministic (no API key needed, ever):** GWA Calculator Autofill, HTML
  Layout Card Populator.
- **LLM-assisted, no API key needed by default:** GWA Level 1 Report, Helio
  Pre-Dev Report, Helio Feasibility Tiers, Land Use Prompt Builder. Each of
  these loads the corresponding `SKILL.md` from `SKILLS_ROOT` and, by default,
  runs in **manual mode**: the app composes the full prompt (skill
  instructions + your inputs + extracted file text) and shows a "Copy Prompt"
  button. You paste it into Claude.ai or Claude Code yourself — free, under
  your existing plan — then paste the response back in to get a formatted
  `.docx` download (or, for Land Use Prompt Builder, just copy Claude's
  response directly).

  If you'd rather the app call Claude automatically end-to-end, set
  `ANTHROPIC_API_KEY` in `backend/.env` — the older one-click `/generate`,
  `/assemble`, and `/extract` endpoints still exist and work once a key is
  present, but the frontend UI currently only wires up the manual flow.

## Deployment

The frontend and backend deploy to two separate hosts — Vercel is a great fit
for the static React build, but its serverless functions time out at 10s on
the free tier, which is too short for some LLM-assisted report generations.
The FastAPI backend instead runs as a regular long-lived web service on
Render (or Railway — same idea, different dashboard).

### 1. Backend → Render

1. Push this repo to GitHub (see below).
2. In the [Render dashboard](https://dashboard.render.com), **New → Blueprint**,
   point it at this repo. It reads `render.yaml` at the repo root automatically.
3. Set the `ANTHROPIC_API_KEY` env var when prompted (marked `sync: false` in
   the blueprint, so Render will ask for it rather than committing it).
4. Once deployed, copy the service's public URL (e.g.
   `https://claude-skills-hub-api.onrender.com`).
5. Back in Render's dashboard for that service, set `FRONTEND_ORIGINS` to your
   Vercel URL(s) from step 2 below (comma-separated if there's more than one),
   so CORS allows the deployed frontend to call it.

### 2. Frontend → Vercel

1. In the [Vercel dashboard](https://vercel.com/new), import this GitHub repo.
2. Set **Root Directory** to `frontend`.
3. Add an env var `VITE_API_BASE_URL` = your Render backend URL from step 1
   above (no trailing slash).
4. Deploy. `frontend/vercel.json` handles the SPA rewrite so client-side
   routes like `/gwa-autofill` work on refresh.

### 3. GitHub

```bash
gh auth login          # one-time interactive browser sign-in
gh repo create claude-skills-hub --source=. --public --push
```
(or `--private` instead of `--public`, depending on preference).
