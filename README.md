# CivicGuide - Election Process Education Assistant

CivicGuide is an interactive WebApp designed to help users understand the election process, timelines, and steps in a neutral, accessible, and easy-to-follow way.

## Approach and Logic
CivicGuide uses a specialized system prompt with the Google Gemini API to adopt the persona of a highly accessible, neutral, and encouraging election process assistant. It determines the user's current step in the election journey and provides clear, step-by-step guidance formatted with bullet points and short paragraphs, concluding with a follow-up question to maintain engagement.

## Tech Stack
- **Frontend**: Vite + React
- **Backend**: FastAPI (Python)
- **AI Integration**: Google Gemini API (`gemini-1.5-flash`)
- **Deployment**: Google Cloud Run (Multi-stage Dockerfile)

## How to Run Locally

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- Google Gemini API Key

### Setup Instructions

1. **Clone the repository** (if not already done).
2. **Environment Variables**:
   Copy `.env.example` to `.env` and add your Gemini API Key:
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

1. **Code Quality**: Structured the app with distinct `frontend/` and `backend/` directories. Used Pydantic for strict request/response validation in Python and implemented clear component architecture in React.
2. **Security**: Implemented a rate limiter (`slowapi`) in the FastAPI backend, strict CORS origins, and sanitized all Markdown/HTML rendered from the AI using `DOMPurify` to prevent XSS. Secrets are managed via `.env`.
3. **Efficiency**: Implemented an input debounce mechanism in React to prevent API spam, optimized state management, and used asynchronous (`async/await`) API calls in the backend to ensure non-blocking performance.
4. **Testing**: Included automated tests using `pytest` for the backend API (validating payloads and health checks) and `vitest` for the frontend React components.
5. **Accessibility (a11y)**: Built the UI with semantic HTML. Included `aria-live="polite"` for dynamic chat announcements, `aria-label` tags for all interactive elements, ensured full keyboard navigability, and maintained high WCAG color contrast.
6. **Google Services**: Meaningfully integrated the Google Gemini API as the core logic engine with a strict system prompt, and optimized the application for Google Cloud Run deployment using a multi-stage Dockerfile to keep the footprint minimal.
