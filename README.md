# Fact Checker

React + FastAPI app for an upload-first fact-checking workflow:

1. Upload a screenshot, audio/video clip, or social media link.
2. Extract visible text or transcribe spoken content.
3. Analyze bait-like or misleading framing.
4. Compare against broader reporting.
5. Return a neutral summary.

## Structure

```text
backend/
  api/         FastAPI routes
  core/        Settings and app config
  schemas/     Request and response models
  services/    OCR, transcription, framing, search, summarization pipeline
  scripts/     Smoke tests for live backend services
  tests/       Basic API tests
frontend/
  src/api/         Backend client helpers
  src/components/  UI building blocks
```

## Backend

### Windows

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Linux/Mac

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

For video uploads, install the `ffmpeg` system binary and make sure it is on `PATH`.

Ubuntu / WSL:

```bash
sudo apt update
sudo apt install ffmpeg
```

Required environment variables in the repo-root `.env`:

```env
GEMINI_API_KEY=
TAVILY_API_KEY=
FRONTEND_ORIGIN=http://localhost:5173
```

Current backend inputs:

- screenshot/image upload
- audio upload
- video upload
- social media link

The `/api/analyze` route routes images through OCR, audio/video through transcription, and links through Tavily extraction before running the shared framing/search/summary pipeline.

## Smoke Tests

Run these from `backend/` after activating the virtualenv:

```bash
python scripts/ocr_smoke_test.py
python scripts/analyzer_smoke_test.py
python scripts/search_smoke_test.py
python scripts/summary_smoke_test.py
python scripts/media_smoke_test.py /absolute/path/to/clip.mp3 or clip.mp4
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` requests to `http://localhost:8000`.

## Tests

From `backend/`:

```bash
python -m pytest
```
