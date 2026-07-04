import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

def generate_uuid() -> str:
    return uuid.uuid4().hex

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    xp: int = Field(default=0)
    level: int = Field(default=1)
    streak: int = Field(default=0)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    subjects: List["Subject"] = Relationship(back_populates="user", cascade_delete=True)
    study_plans: List["StudyPlan"] = Relationship(back_populates="user", cascade_delete=True)
    tutor_sessions: List["TutorChatSession"] = Relationship(back_populates="user", cascade_delete=True)
    quizzes: List["Quiz"] = Relationship(back_populates="user", cascade_delete=True)
    activity_logs: List["AgentActivityLog"] = Relationship(back_populates="user", cascade_delete=True)

class Subject(SQLModel, table=True):
    __tablename__ = "subjects"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", ondelete="CASCADE")
    name: str
    difficulty: int = Field(default=3) # 1-5 scale
    current_grade: float = Field(default=100.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="subjects")
    exams: List["Exam"] = Relationship(back_populates="subject", cascade_delete=True)
    study_plan_items: List["StudyPlanItem"] = Relationship(back_populates="subject", cascade_delete=True)
    quizzes: List["Quiz"] = Relationship(back_populates="subject", cascade_delete=True)

class Exam(SQLModel, table=True):
    __tablename__ = "exams"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    subject_id: str = Field(foreign_key="subjects.id", ondelete="CASCADE")
    name: str
    date: date
    weight: float = Field(default=10.0) # weight in percentage (0-100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    subject: Optional[Subject] = Relationship(back_populates="exams")

class StudyPlan(SQLModel, table=True):
    __tablename__ = "study_plans"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", ondelete="CASCADE")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="study_plans")
    items: List["StudyPlanItem"] = Relationship(back_populates="study_plan", cascade_delete=True)

class StudyPlanItem(SQLModel, table=True):
    __tablename__ = "study_plan_items"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    plan_id: str = Field(foreign_key="study_plans.id", ondelete="CASCADE")
    subject_id: str = Field(foreign_key="subjects.id", ondelete="CASCADE")
    date: date
    start_time: str # e.g. "09:00"
    duration_minutes: int
    topic: str
    priority_score: float = Field(default=0.0)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    study_plan: Optional[StudyPlan] = Relationship(back_populates="items")
    subject: Optional[Subject] = Relationship(back_populates="study_plan_items")

class TutorChatSession(SQLModel, table=True):
    __tablename__ = "tutor_chat_sessions"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", ondelete="CASCADE")
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="tutor_sessions")
    messages: List["TutorMessage"] = Relationship(back_populates="session", cascade_delete=True)

class TutorMessage(SQLModel, table=True):
    __tablename__ = "tutor_messages"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    session_id: str = Field(foreign_key="tutor_chat_sessions.id", ondelete="CASCADE")
    sender: str # "user" or "assistant"
    content: str
    agent_name: Optional[str] = Field(default=None)
    logs: Optional[str] = Field(default=None) # Socratic logs or intermediate agent outputs
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    session: Optional[TutorChatSession] = Relationship(back_populates="messages")

class Quiz(SQLModel, table=True):
    __tablename__ = "quizzes"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", ondelete="CASCADE")
    subject_id: str = Field(foreign_key="subjects.id", ondelete="CASCADE")
    score: int
    total_questions: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="quizzes")
    subject: Optional[Subject] = Relationship(back_populates="quizzes")
    questions: List["QuizQuestion"] = Relationship(back_populates="quiz", cascade_delete=True)

class QuizQuestion(SQLModel, table=True):
    __tablename__ = "quiz_questions"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    quiz_id: str = Field(foreign_key="quizzes.id", ondelete="CASCADE")
    question_text: str
    options: str # Store as JSON list string
    correct_option: int
    explanation: Optional[str] = Field(default=None)
    user_answer: Optional[int] = Field(default=None)
    is_correct: Optional[bool] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    quiz: Optional[Quiz] = Relationship(back_populates="questions")

class AgentActivityLog(SQLModel, table=True):
    __tablename__ = "agent_activity_logs"
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="users.id", ondelete="CASCADE")
    agent_name: str
    activity_type: str
    message: str
    details: Optional[str] = Field(default=None) # Store as JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="activity_logs")

# Pydantic schemas for request/response bodies (non-table SQLModels)
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

class SubjectCreate(BaseModel):
    name: str
    difficulty: int
    current_grade: Optional[float] = 100.0

class ExamCreate(BaseModel):
    subject_id: str
    name: str
    date: date
    weight: float

class StudyPlanItemUpdate(BaseModel):
    is_completed: bool

class TutorMessageCreate(BaseModel):
    content: str

class QuizSubmission(BaseModel):
    answers: List[int] # List of chosen options matching question indices
