# Fact Checker

React + FastAPI scaffold for an upload-first fact-checking workflow:

1. Upload a screenshot or post image.
2. Extract visible text.
3. Analyze bait-like or misleading framing.
4. Compare against broader reporting.
5. Return a neutral summary.

## Structure

```text
backend/
  api/         FastAPI routes
  core/        Settings and app config
  schemas/     Request and response models
  services/    OCR, framing, search, summarization pipeline
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

The backend currently uses placeholder service implementations so the API is runnable before Gemini and Tavily are wired in.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` requests to `http://localhost:8000`.

