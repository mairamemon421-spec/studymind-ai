import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User, Subject, Exam, StudyPlan, PlanSession, Quiz, QuizQuestion, AgentLog
from app.auth import create_access_token

def test_full_integration_workflow():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def _get_test_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db

    async def run_test():
        # 1. Setup tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 2. Setup mock user and auth
        async with TestingSessionLocal() as db:
            user_id = "integration-user-uuid"
            user = User(
                id=user_id,
                email="integration@example.com",
                full_name="Integration User",
                study_hours_per_day=4,
            )
            db.add(user)
            await db.commit()

            token = create_access_token({"sub": user_id})
            headers = {"Authorization": f"Bearer {token}"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 3. Create Subject
            subj_res = await client.post(
                "/api/subjects",
                json={"name": "Biology", "description": "Cellular biology and genetics", "difficulty": 3},
                headers=headers
            )
            assert subj_res.status_code == 201
            subject = subj_res.json()
            subj_id = subject["id"]

            # 4. Create Exam
            exam_res = await client.post(
                "/api/exams",
                json={"subject_id": subj_id, "title": "Genetics Midterm", "exam_date": "2026-07-20", "importance": 4},
                headers=headers
            )
            assert exam_res.status_code == 201
            exam = exam_res.json()

            # 5. Generate Study Plan
            plan_res = await client.post(
                "/api/plans/generate",
                json={"title": "Biology Study Schedule", "weeks_ahead": 2},
                headers=headers
            )
            assert plan_res.status_code == 201
            plan = plan_res.json()
            plan_id = plan["id"]
            assert len(plan["sessions"]) > 0

            # 6. Complete a session
            session_id = plan["sessions"][0]["id"]
            complete_res = await client.post(
                f"/api/plans/{plan_id}/complete-session",
                json={"session_id": session_id, "notes": "Learned cell structures"},
                headers=headers
            )
            assert complete_res.status_code == 200

            # 7. Start Tutor Session
            tutor_session_res = await client.post(
                "/api/tutor/sessions",
                json={"subject_id": subj_id, "title": "Bio Chat"},
                headers=headers
            )
            assert tutor_session_res.status_code == 201
            tutor_session = tutor_session_res.json()
            tutor_session_id = tutor_session["id"]

            # 8. Send Tutor Message
            tutor_msg_res = await client.post(
                f"/api/tutor/sessions/{tutor_session_id}/messages",
                json={"content": "Explain mitosis vs meiosis"},
                headers=headers
            )
            assert tutor_msg_res.status_code == 200
            tutor_reply = tutor_msg_res.json()
            assert len(tutor_reply["content"]) > 0

            # 9. Generate Quiz
            quiz_res = await client.post(
                "/api/quiz/generate",
                json={"subject_id": subj_id, "topic": "Genetics", "difficulty": 3, "num_questions": 3},
                headers=headers
            )
            assert quiz_res.status_code == 201
            quiz = quiz_res.json()
            quiz_id = quiz["id"]
            assert len(quiz["questions"]) == 3

            # 10. Submit Quiz Answers
            answers = [
                {"question_id": q["id"], "answer": "Option A"}
                for q in quiz["questions"]
            ]
            submit_res = await client.post(
                f"/api/quiz/{quiz_id}/submit",
                json={"answers": answers},
                headers=headers
            )
            assert submit_res.status_code == 200
            result = submit_res.json()
            assert result["quiz_id"] == quiz_id

            # 11. Retrieve Dashboard Progress
            progress_res = await client.get("/api/progress", headers=headers)
            assert progress_res.status_code == 200
            progress = progress_res.json()
            assert "streak_days" in progress

            # 12. Retrieve Agent Activity Logs
            logs_res = await client.get("/api/logs", headers=headers)
            assert logs_res.status_code == 200
            logs_data = logs_res.json()
            assert logs_data["total"] > 0

            # 13. Export study plan to PDF
            pdf_res = await client.get(f"/api/export/pdf/{plan_id}", headers=headers)
            assert pdf_res.status_code == 200
            assert pdf_res.headers["content-type"] == "application/pdf"

        # Drop tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    try:
        asyncio.run(run_test())
    finally:
        app.dependency_overrides.clear()
