import asyncio
from app.agents.priority_agent import PriorityAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.tutor_agent import TutorAgent
from app.agents.quiz_agent import QuizAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.progress_agent import ProgressAgent

def test_priority_agent():
    async def run_test():
        agent = PriorityAgent()
        subjects = [
            {"id": "s1", "name": "Math", "difficulty": 4, "mastery_score": 0.3},
            {"id": "s2", "name": "History", "difficulty": 2, "mastery_score": 0.8}
        ]
        exams = [
            {"subject_id": "s1", "exam_date": "2026-07-10", "importance": 5, "title": "Math Final"}
        ]
        result = await agent.rank_subjects(subjects, exams, user_id="test_user")
        assert "ranked" in result
        assert len(result["ranked"]) == 2
        assert result["ranked"][0]["subject_name"] == "Math"
    
    asyncio.run(run_test())

def test_planner_agent():
    async def run_test():
        agent = PlannerAgent()
        ranked_subjects = [
            {"subject_id": "s1", "subject_name": "Math", "priority_score": 0.9, "reasoning": "High urgency"},
            {"subject_id": "s2", "subject_name": "History", "priority_score": 0.4, "reasoning": "Normal"}
        ]
        result = await agent.create_schedule(ranked_subjects, study_hours_per_day=4, weeks_ahead=1, user_id="test_user")
        assert "sessions" in result
        assert len(result["sessions"]) > 0
    
    asyncio.run(run_test())

def test_coordinator_agent():
    async def run_test():
        agent = CoordinatorAgent()
        subjects = [
            {"id": "s1", "name": "Math", "difficulty": 4, "mastery_score": 0.3},
            {"id": "s2", "name": "History", "difficulty": 2, "mastery_score": 0.8}
        ]
        exams = [
            {"subject_id": "s1", "exam_date": "2026-07-10", "importance": 5, "title": "Math Final"}
        ]
        result = await agent.generate_plan(subjects, exams, study_hours_per_day=4, weeks_ahead=1, user_id="test_user")
        assert "sessions" in result
        assert "coordinator_notes" in result
        assert len(result["logs"]) >= 2
    
    asyncio.run(run_test())

def test_tutor_agent():
    async def run_test():
        agent = TutorAgent()
        history = [
            {"role": "user", "content": "Explain gravity"},
            {"role": "assistant", "content": "Gravity is a force..."}
        ]
        result = await agent.chat(
            subject_name="Physics",
            message="What is acceleration due to gravity?",
            history=history,
            user_id="test_user"
        )
        assert "reply" in result
        assert len(result["reply"]) > 0
    
    asyncio.run(run_test())

def test_quiz_agent():
    async def run_test():
        agent = QuizAgent()
        result = await agent.generate_quiz(
            subject_name="Physics",
            topic="Gravity",
            difficulty=3,
            num_questions=3,
            user_id="test_user"
        )
        assert "questions" in result
        assert len(result["questions"]) == 3
    
    asyncio.run(run_test())

def test_analytics_agent():
    async def run_test():
        agent = AnalyticsAgent()
        quiz_data = {"subject_name": "Math", "topic": "Calculus", "difficulty": 3}
        questions_with_answers = [
            {"question_text": "1+1?", "is_correct": True},
            {"question_text": "2+2?", "is_correct": False}
        ]
        result = await agent.analyze_quiz(quiz_data, questions_with_answers, user_id="test_user")
        assert result["score"] == 0.5
        assert result["correct"] == 1
        assert result["total"] == 2
        assert "feedback" in result
    
    asyncio.run(run_test())

def test_progress_agent():
    async def run_test():
        agent = ProgressAgent()
        sessions = [
            {"subject_name": "Math", "session_date": "2026-06-27", "duration_minutes": 90, "completed": True},
            {"subject_name": "Math", "session_date": "2026-06-28", "duration_minutes": 90, "completed": True}
        ]
        subjects = [{"name": "Math", "mastery_score": 0.4}]
        exams = [{"subject_id": "s1", "title": "Math Final", "exam_date": "2026-07-05", "importance": 5}]
        result = await agent.calculate_progress(sessions, subjects, exams, user_id="test_user")
        assert "streak_days" in result
        assert "overall_readiness" in result
    
    asyncio.run(run_test())
