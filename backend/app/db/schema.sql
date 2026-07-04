-- Create Profiles / Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    full_name VARCHAR(255),
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    streak INTEGER DEFAULT 0,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Subjects Table
CREATE TABLE IF NOT EXISTS subjects (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    difficulty INTEGER NOT NULL CHECK (difficulty >= 1 AND difficulty <= 5),
    current_grade NUMERIC(5,2) DEFAULT 100.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Exams Table
CREATE TABLE IF NOT EXISTS exams (
    id VARCHAR(255) PRIMARY KEY,
    subject_id VARCHAR(255) REFERENCES subjects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    weight NUMERIC(5,2) NOT NULL CHECK (weight >= 0.00 AND weight <= 100.00),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Study Plans Table
CREATE TABLE IF NOT EXISTS study_plans (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Study Plan Items Table
CREATE TABLE IF NOT EXISTS study_plan_items (
    id VARCHAR(255) PRIMARY KEY,
    plan_id VARCHAR(255) REFERENCES study_plans(id) ON DELETE CASCADE,
    subject_id VARCHAR(255) REFERENCES subjects(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    start_time VARCHAR(10) NOT NULL,
    duration_minutes INTEGER NOT NULL,
    topic TEXT NOT NULL,
    priority_score NUMERIC(5,2) DEFAULT 0.00,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Tutor Chat Sessions Table
CREATE TABLE IF NOT EXISTS tutor_chat_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Tutor Messages Table
CREATE TABLE IF NOT EXISTS tutor_messages (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES tutor_chat_sessions(id) ON DELETE CASCADE,
    sender VARCHAR(20) NOT NULL CHECK (sender IN ('user', 'assistant')),
    content TEXT NOT NULL,
    agent_name VARCHAR(100),
    logs TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Quizzes Table
CREATE TABLE IF NOT EXISTS quizzes (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    subject_id VARCHAR(255) REFERENCES subjects(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Quiz Questions Table
CREATE TABLE IF NOT EXISTS quiz_questions (
    id VARCHAR(255) PRIMARY KEY,
    quiz_id VARCHAR(255) REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    options TEXT NOT NULL, -- JSON string representing options list
    correct_option INTEGER NOT NULL,
    explanation TEXT,
    user_answer INTEGER,
    is_correct BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Agent Activity Logs Table
CREATE TABLE IF NOT EXISTS agent_activity_logs (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    details TEXT, -- JSON string representing activity detail logs
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
