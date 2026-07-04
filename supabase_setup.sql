-- StudyMind AI — PostgreSQL Setup Script for Supabase

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── 1. Create public.users table (linked to auth.users) ──────────────────────
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    study_hours_per_day INTEGER DEFAULT 4,
    timezone VARCHAR(100) DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 2. Trigger function to automatically sync new signups from auth.users ─────
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name, study_hours_per_day)
    VALUES (
        new.id,
        new.email,
        coalesce(new.raw_user_meta_data->>'full_name', ''),
        coalesce((new.raw_user_meta_data->>'study_hours_per_day')::integer, 4)
    );
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create the trigger
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ─── 3. Create all other business tables ──────────────────────────────────────

-- Subjects
CREATE TABLE IF NOT EXISTS public.subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color VARCHAR(20) DEFAULT '#9047ff',
    icon VARCHAR(50) DEFAULT 'BookOpen',
    difficulty INTEGER DEFAULT 3 CHECK (difficulty BETWEEN 1 AND 5),
    mastery_score FLOAT DEFAULT 0.0 CHECK (mastery_score BETWEEN 0.0 AND 1.0),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Exams
CREATE TABLE IF NOT EXISTS public.exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES public.subjects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    exam_date DATE NOT NULL,
    importance INTEGER DEFAULT 3 CHECK (importance BETWEEN 1 AND 5),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Study Plans
CREATE TABLE IF NOT EXISTS public.study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    coordinator_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Study Plan Sessions
CREATE TABLE IF NOT EXISTS public.plan_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES public.study_plans(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,
    subject_name VARCHAR(255) NOT NULL,
    topic VARCHAR(500),
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_minutes INTEGER NOT NULL,
    priority_score FLOAT DEFAULT 0.5,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    notes TEXT
);

-- Chat Sessions
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,
    title VARCHAR(255) DEFAULT 'New Chat',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Messages
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quizzes
CREATE TABLE IF NOT EXISTS public.quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,
    subject_name VARCHAR(255) NOT NULL,
    topic VARCHAR(500),
    difficulty INTEGER DEFAULT 3,
    total_questions INTEGER DEFAULT 5,
    status VARCHAR(50) DEFAULT 'pending',
    score FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Quiz Questions
CREATE TABLE IF NOT EXISTS public.quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES public.quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'multiple_choice',
    options JSONB,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    user_answer TEXT,
    is_correct BOOLEAN,
    order_index INTEGER DEFAULT 0
);

-- Agent Logs
CREATE TABLE IF NOT EXISTS public.agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    agent_name VARCHAR(100) NOT NULL,
    action VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    input_summary TEXT,
    output_summary TEXT,
    duration_ms INTEGER,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_subjects_user ON public.subjects(user_id);
CREATE INDEX IF NOT EXISTS idx_exams_user ON public.exams(user_id);
CREATE INDEX IF NOT EXISTS idx_exams_subject ON public.exams(subject_id);
CREATE INDEX IF NOT EXISTS idx_plans_user ON public.study_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_plan ON public.plan_sessions(plan_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON public.plan_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON public.chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON public.chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_user ON public.quizzes(user_id);
CREATE INDEX IF NOT EXISTS idx_questions_quiz ON public.quiz_questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_logs_user ON public.agent_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_created ON public.agent_logs(created_at DESC);

-- ─── 4. Row Level Security (RLS) Configuration ──────────────────────────────

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plan_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_logs ENABLE ROW LEVEL SECURITY;

-- ─── 5. Create RLS Policies ──────────────────────────────────────────────────

-- Policies for public.users
CREATE POLICY "Allow users to read their own profiles" ON public.users 
    FOR SELECT TO authenticated USING (auth.uid() = id);

CREATE POLICY "Allow users to update their own profiles" ON public.users 
    FOR UPDATE TO authenticated USING (auth.uid() = id);

-- Policies for subjects
CREATE POLICY "Allow users to manage their own subjects" ON public.subjects 
    FOR ALL TO authenticated USING (auth.uid() = user_id);

-- Policies for exams
CREATE POLICY "Allow users to manage their own exams" ON public.exams 
    FOR ALL TO authenticated USING (auth.uid() = user_id);

-- Policies for study_plans
CREATE POLICY "Allow users to manage their own plans" ON public.study_plans 
    FOR ALL TO authenticated USING (auth.uid() = user_id);

-- Policies for plan_sessions (tied to study_plans ownership)
CREATE POLICY "Allow users to manage their plan sessions" ON public.plan_sessions 
    FOR ALL TO authenticated USING (
        plan_id IN (SELECT id FROM public.study_plans WHERE user_id = auth.uid())
    );

-- Policies for chat_sessions
CREATE POLICY "Allow users to manage their chat sessions" ON public.chat_sessions 
    FOR ALL TO authenticated USING (auth.uid() = user_id);

-- Policies for chat_messages (tied to chat_sessions ownership)
CREATE POLICY "Allow users to manage their chat messages" ON public.chat_messages 
    FOR ALL TO authenticated USING (
        session_id IN (SELECT id FROM public.chat_sessions WHERE user_id = auth.uid())
    );

-- Policies for quizzes
CREATE POLICY "Allow users to manage their quizzes" ON public.quizzes 
    FOR ALL TO authenticated USING (auth.uid() = user_id);

-- Policies for quiz_questions (tied to quizzes ownership)
CREATE POLICY "Allow users to manage their quiz questions" ON public.quiz_questions 
    FOR ALL TO authenticated USING (
        quiz_id IN (SELECT id FROM public.quizzes WHERE user_id = auth.uid())
    );

-- Policies for agent_logs
CREATE POLICY "Allow users to manage their agent logs" ON public.agent_logs 
    FOR ALL TO authenticated USING (auth.uid() = user_id);
