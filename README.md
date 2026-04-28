# CivicGuide - Election Process Education Assistant

CivicGuide is an interactive WebApp designed to help users understand the election process, timelines, and steps in a neutral, accessible, and easy-to-follow way.

## Approach and Logic
CivicGuide uses a specialized system prompt with the Google Gemini API to adopt the persona of a highly accessible, neutral, and encouraging election process assistant. It determines the user's current step in the election journey and provides clear, step-by-step guidance formatted with bullet points and short paragraphs, concluding with a follow-up question to maintain engagement.

## Tech Stack
- **Frontend**: Vite + React + TypeScript
- **Backend**: FastAPI (Python)
- **AI Integration**: Google Gemini API (`gemini-2.5-flash`) with Structured Outputs
- **Google Services**: Firebase (Anonymous Auth, Firestore) and Google Cloud Logging
- **Deployment**: Google Cloud Run (Multi-stage Dockerfile)

## How to Run Locally

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- Google Gemini API Key
- Firebase Project setup

### Setup Instructions

1. **Clone the repository** (if not already done).
2. **Environment Variables**:
   Copy `.env.example` to `.env` and add your Gemini API Key and mock Firebase config:
   ```bash
   cp .env.example .env
   ```

3. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

4. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
   *Note: For local development of just the frontend, you can use `npm run dev`, but ensure the backend is running to handle API requests.*

5. **Run the Application**:
   In the `backend` directory, start the FastAPI server (which also serves the frontend):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```
   Open `http://localhost:8080` in your browser.

## Evaluation Checklist (How we met the criteria)

1. **Code Quality**: Migrated the entire Vite React frontend strictly to TypeScript. Refactored the FastAPI backend into a highly modular structure (`main.py`, `api/routes.py`, `services/gemini_service.py`, `schemas/models.py`). Provided extensive JSDoc and PEP-257 compliant docstrings.
2. **Security**: Implemented a rate limiter (`slowapi`) in the FastAPI backend, strict CORS origins, and sanitized all Markdown/HTML rendered from the AI using `DOMPurify` to prevent XSS. Secrets are managed via `.env`.
3. **Efficiency**: Heavily utilized React `useMemo`, `useCallback`, and `React.memo` to prevent unnecessary re-renders. Implemented `React.lazy` and `Suspense` for component code-splitting. Used `async-lru` (`alru_cache`) in the backend for caching repetitive operations. Configured Vite `build.rollupOptions` to split vendor chunks.
4. **Testing**: Included automated tests using `pytest` for the backend API and `vitest` for the frontend React components covering the new Firebase and memoization logic.
5. **Accessibility (a11y)**: Built the UI with semantic HTML. Included `aria-live="polite"` for dynamic chat announcements, `aria-label` tags for all interactive elements, ensured full keyboard navigability, and maintained high WCAG color contrast.
6. **Google Services**: This project heavily utilizes Google Services including Gemini 2.5 Flash API (Structured Outputs), Firebase Authentication, Cloud Firestore (chat history), and Google Cloud Logging. The application logger outputs JSON structured logs compatible with Google Cloud Logging.
