from datetime import date, datetime, time
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, field_validator
import uuid


# ─── Auth ───────────────────────────────────────────────────────────────────
# Note: sign-up and login are handled by Supabase Auth on the frontend.
# The backend only exposes GET /api/auth/me using the Supabase JWT.

class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    study_hours_per_day: int = 4
    timezone: str = "UTC"
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Subjects ────────────────────────────────────────────────────────────────

class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#9047ff"
    icon: str = "BookOpen"
    difficulty: int = 3

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    difficulty: Optional[int] = None
    mastery_score: Optional[float] = None

class SubjectOut(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    color: str
    icon: str
    difficulty: int
    mastery_score: float
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Exams ───────────────────────────────────────────────────────────────────

class ExamCreate(BaseModel):
    subject_id: str
    title: str
    exam_date: date
    importance: int = 3
    notes: Optional[str] = None

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    exam_date: Optional[date] = None
    importance: Optional[int] = None
    notes: Optional[str] = None

class ExamOut(BaseModel):
    id: str
    user_id: str
    subject_id: str
    title: str
    exam_date: date
    importance: int
    notes: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Study Plans ─────────────────────────────────────────────────────────────

class PlanGenerateRequest(BaseModel):
    title: Optional[str] = None
    weeks_ahead: int = 2

class PlanSessionOut(BaseModel):
    id: str
    plan_id: str
    subject_id: Optional[str]
    subject_name: str
    topic: Optional[str]
    session_date: date
    start_time: time
    end_time: time
    duration_minutes: int
    priority_score: float
    completed: bool
    notes: Optional[str]
    model_config = {"from_attributes": True}

class PlanOut(BaseModel):
    id: str
    user_id: str
    title: str
    start_date: date
    end_date: date
    status: str
    coordinator_notes: Optional[str]
    created_at: datetime
    sessions: List[PlanSessionOut] = []
    model_config = {"from_attributes": True}

class SessionCompleteRequest(BaseModel):
    session_id: str
    notes: Optional[str] = None


# ─── Chat ────────────────────────────────────────────────────────────────────

class ChatSessionCreate(BaseModel):
    subject_id: Optional[str] = None
    title: str = "New Chat"

class ChatMessageCreate(BaseModel):
    content: str

class ChatMessageOut(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime
    model_config = {"from_attributes": True}

class ChatSessionOut(BaseModel):
    id: str
    user_id: str
    subject_id: Optional[str]
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageOut] = []
    model_config = {"from_attributes": True}

class ChatSessionListOut(BaseModel):
    id: str
    user_id: str
    subject_id: Optional[str]
    title: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ─── Quiz ────────────────────────────────────────────────────────────────────

class QuizGenerateRequest(BaseModel):
    subject_id: str
    topic: Optional[str] = None
    difficulty: int = 3
    num_questions: int = 5

class QuizQuestionOut(BaseModel):
    id: str
    quiz_id: str
    question_text: str
    question_type: str
    options: Optional[List[str]]
    correct_answer: Optional[str] = None  # hidden during quiz
    explanation: Optional[str] = None
    user_answer: Optional[str]
    is_correct: Optional[bool]
    order_index: int
    model_config = {"from_attributes": True}

class QuizOut(BaseModel):
    id: str
    user_id: str
    subject_id: Optional[str]
    subject_name: str
    topic: Optional[str]
    difficulty: int
    total_questions: int
    status: str
    score: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]
    questions: List[QuizQuestionOut] = []
    model_config = {"from_attributes": True}

class QuizSubmitAnswer(BaseModel):
    question_id: str
    answer: str

class QuizSubmitRequest(BaseModel):
    answers: List[QuizSubmitAnswer]

class QuizResultOut(BaseModel):
    quiz_id: str
    score: float
    correct: int
    total: int
    percentage: float
    weak_areas: List[str]
    feedback: str
    questions: List[QuizQuestionOut]


# ─── Agent Logs ──────────────────────────────────────────────────────────────

class AgentLogOut(BaseModel):
    id: str
    user_id: Optional[str]
    agent_name: str
    action: str
    status: str
    input_summary: Optional[str]
    output_summary: Optional[str]
    duration_ms: Optional[int]
    created_at: datetime
    model_config = {"from_attributes": True}

class AgentLogsResponse(BaseModel):
    logs: List[AgentLogOut]
    total: int
    page: int
    page_size: int


# ─── Progress ────────────────────────────────────────────────────────────────

class ProgressOut(BaseModel):
    streak_days: int
    total_sessions_completed: int
    sessions_today: int
    hours_studied_week: float
    readiness_scores: dict  # subject_name -> float
    upcoming_exams: List[ExamOut]
    overall_readiness: float
