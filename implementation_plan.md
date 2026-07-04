# Multi-Agent AI Study Planner & Tutor — Implementation Plan

A full-stack study planning application with a multi-agent Gemini AI backend (FastAPI + SQLite/Supabase) and a premium glassmorphism React frontend (Vite + TypeScript + Tailwind CSS v3).

## User Review Required

> [!IMPORTANT]
> **Tailwind CSS v3**: The `package.json` already lists `tailwindcss@^3.4.1`, `postcss`, and `autoprefixer` as dependencies. We need to add `tailwind.config.js` and `postcss.config.js` configuration files. The task explicitly calls for Tailwind v3 (not v4).

> [!IMPORTANT]
> **Gemini API Key**: The `.env` file has `GEMINI_API_KEY=` (empty). All AI agent features will return **mock/simulated responses** when no key is configured, and real Gemini responses when a key is present. This keeps the app fully functional for development without an API key.

> [!WARNING]
> **No `react-router-dom`** is installed. We will need to install it for page routing. We will also install `react-hot-toast` for notifications.

## Open Questions

1. **Authentication scope**: The plan includes local JWT-based mock auth. Should we also wire up Supabase Auth from the start, or keep that strictly for Phase 6?  
   *Current assumption: Mock auth first, Supabase toggle in Phase 6.*

2. **PDF Export**: ReportLab generates server-side PDFs. Is downloading a PDF via the browser sufficient, or do you need email delivery?  
   *Current assumption: Browser download only.*

---

## Proposed Changes

### Phase 1: Complete Project Scaffolding & Setup

#### [MODIFY] [package.json](file:///c:/Users/maira/Desktop/antigravity_workspace/frontend/package.json)
- Add `react-router-dom`, `react-hot-toast` dependencies

#### [NEW] `frontend/tailwind.config.js`
- Tailwind v3 config with custom color palette (deep purples, teals, glassmorphism-friendly colors), dark mode via `class` strategy

#### [NEW] `frontend/postcss.config.js`
- PostCSS config wiring Tailwind and Autoprefixer

#### [NEW] `backend/app/__init__.py`, `backend/app/main.py`
- FastAPI app factory with CORS, lifespan events for DB init

#### [NEW] `backend/app/config.py`
- Pydantic Settings loading from `.env`

#### [NEW] `.gitignore` (update)
- Ensure `venv/`, `node_modules/`, `*.db`, `.env` are ignored

---

### Phase 2: Database Schema & Local Mock Setup

#### [NEW] `backend/schema.sql`
- Full PostgreSQL-compatible schema: `users`, `subjects`, `exams`, `study_plans`, `plan_sessions`, `chat_sessions`, `chat_messages`, `quizzes`, `quiz_questions`, `quiz_attempts`, `agent_logs`

#### [NEW] `backend/app/database.py`
- Async SQLAlchemy engine factory supporting both `sqlite+aiosqlite` and PostgreSQL (Supabase)
- Session dependency for FastAPI

#### [NEW] `backend/app/models.py`
- SQLAlchemy ORM models matching `schema.sql`

#### [NEW] `backend/app/schemas.py`
- Pydantic request/response schemas for all API endpoints

---

### Phase 3: Multi-Agent AI Engine (Gemini API)

All agents live under `backend/app/agents/`. Each agent is a Python module with a clear interface. When `GEMINI_API_KEY` is empty, agents return structured mock data.

#### [NEW] `backend/app/agents/__init__.py`
#### [NEW] `backend/app/agents/base.py`
- Base agent class with Gemini client initialization, mock fallback, and structured logging

#### [NEW] `backend/app/agents/priority_agent.py`
- Ranks subjects by urgency (exam proximity, difficulty, current mastery)
- Input: list of subjects + exams → Output: ranked priority list with scores

#### [NEW] `backend/app/agents/planner_agent.py`
- Creates a weekly study schedule based on priority rankings and available hours
- Output: structured timetable (day, time slots, subject, topic)

#### [NEW] `backend/app/agents/coordinator_agent.py`
- Orchestrates Priority → Planner pipeline
- Records step-by-step agent activity logs for the frontend feed

#### [NEW] `backend/app/agents/tutor_agent.py`
- Conversational chat agent — explains concepts with simple examples
- Maintains conversation history per session

#### [NEW] `backend/app/agents/quiz_agent.py`
- Generates multiple-choice and short-answer questions for a given subject/topic

#### [NEW] `backend/app/agents/analytics_agent.py`
- Analyzes quiz results, identifies weak areas, suggests focus topics

#### [NEW] `backend/app/agents/progress_agent.py`
- Calculates study streak, daily completion rate, and "readiness score" per subject

---

### Phase 4: Backend API Endpoints

All routers live under `backend/app/routers/`.

#### [NEW] `backend/app/routers/__init__.py`
#### [NEW] `backend/app/routers/auth.py`
- `POST /api/auth/register` — create user (mock, local JWT)
- `POST /api/auth/login` — authenticate, return JWT
- `GET /api/auth/me` — current user profile

#### [NEW] `backend/app/routers/subjects.py`
- CRUD for subjects and exams (`/api/subjects`, `/api/exams`)

#### [NEW] `backend/app/routers/plans.py`
- `POST /api/plans/generate` — trigger Coordinator agent
- `GET /api/plans` — list user's study plans
- `GET /api/plans/{id}` — plan detail with sessions

#### [NEW] `backend/app/routers/tutor.py`
- `POST /api/tutor/sessions` — create chat session
- `POST /api/tutor/sessions/{id}/messages` — send message, get AI reply
- `GET /api/tutor/sessions` — list sessions
- `GET /api/tutor/sessions/{id}` — session with messages

#### [NEW] `backend/app/routers/quiz.py`
- `POST /api/quiz/generate` — generate quiz for a subject
- `POST /api/quiz/{id}/submit` — submit answers, get analytics assessment
- `GET /api/quiz` — list quizzes

#### [NEW] `backend/app/routers/logs.py`
- `GET /api/logs` — agent activity log feed (paginated)

#### [NEW] `backend/app/routers/export.py`
- `GET /api/export/pdf/{plan_id}` — ReportLab PDF export of study plan

#### [NEW] `backend/app/services/pdf_service.py`
- ReportLab PDF generation logic

#### [NEW] `backend/app/auth.py`
- JWT encode/decode helpers, `get_current_user` dependency

---

### Phase 5: Responsive Glassmorphism Frontend (Tailwind v3)

Complete replacement of the default Vite template with a premium dark-mode glassmorphism UI.

#### [MODIFY] `frontend/index.html`
- Update title, meta description, Google Fonts (Inter + JetBrains Mono)

#### [MODIFY] `frontend/src/index.css`
- Tailwind directives (`@tailwind base/components/utilities`), CSS custom properties for glassmorphism, global dark theme

#### [DELETE] `frontend/src/App.css`
- Replaced by Tailwind utility classes

#### [MODIFY] `frontend/src/App.tsx`
- React Router setup, layout with sidebar navigation

#### [MODIFY] `frontend/src/main.tsx`
- Wrap with `BrowserRouter`, `Toaster`

#### [NEW] `frontend/src/lib/api.ts`
- Fetch wrapper pointing to FastAPI backend (`http://localhost:8000/api`)

#### [NEW] `frontend/src/lib/auth.ts`
- Auth context, JWT storage, login/logout helpers

#### [NEW] `frontend/src/components/Layout.tsx`
- Dashboard shell: responsive sidebar, top bar, glassmorphism card containers

#### [NEW] `frontend/src/components/Sidebar.tsx`
- Navigation sidebar with icons (lucide-react), active state, collapse on mobile

#### [NEW] `frontend/src/pages/LoginPage.tsx`
- Glassmorphism login/register form with mock/Supabase toggle

#### [NEW] `frontend/src/pages/DashboardPage.tsx`
- Overview cards: streak, readiness score, upcoming exams, recent activity

#### [NEW] `frontend/src/pages/SubjectsPage.tsx`
- Subject & exam CRUD with glassmorphism cards, difficulty badges

#### [NEW] `frontend/src/pages/PlanPage.tsx`
- AI-generated timetable viewer (weekly grid), session cards

#### [NEW] `frontend/src/pages/AgentLogsPage.tsx`
- Simulated terminal / activity feed showing agent step logs with typing animations

#### [NEW] `frontend/src/pages/TutorPage.tsx`
- Chat panel with message bubbles, typing indicator, session selector

#### [NEW] `frontend/src/pages/QuizPage.tsx`
- Interactive quiz: question cards, progress bar, results summary

#### [NEW] `frontend/src/pages/AnalyticsPage.tsx`
- Recharts charts: quiz scores over time, subject mastery radar, weak areas

---

### Phase 6: Supabase Key Integration

#### [MODIFY] `frontend/src/lib/api.ts`
- Add Supabase client initialization when keys are provided
- Toggle between local API and Supabase direct queries

#### [MODIFY] `backend/app/database.py`
- Auto-detect Supabase URL and switch engine

---

### Phase 7: Verification & Polishing

#### [NEW] `backend/tests/test_auth.py`
- Pytest tests for auth endpoints

#### [NEW] `backend/tests/test_subjects.py`
- Pytest tests for subject/exam CRUD

#### [NEW] `backend/tests/test_agents.py`
- Pytest tests for agent mock responses

---

## Verification Plan

### Automated Tests
```bash
cd backend && python -m pytest tests/ -v
```

### Manual Verification
- Launch backend: `cd backend && uvicorn app.main:app --reload`
- Launch frontend: `cd frontend && npm run dev`
- Use browser subagent to verify:
  - Login/register flow
  - Subject creation
  - Study plan generation
  - Tutor chat interaction
  - Quiz flow
  - Analytics charts render
  - Agent activity log feed
  - PDF export download
  - Responsive layout on mobile viewport
  - Dark mode glassmorphism aesthetics
