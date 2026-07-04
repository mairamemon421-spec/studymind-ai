import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User, Subject, Exam
from app.auth import create_access_token

def test_subject_crud():
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
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with TestingSessionLocal() as db:
            # 1. Create a mock user in database (simulates Supabase Auth trigger)
            user_id = "test-uuid-123"
            user = User(
                id=user_id,
                email="subjectuser@example.com",
                full_name="Subject User",
                study_hours_per_day=3,
            )
            db.add(user)
            await db.commit()

            # 2. Generate a mock token
            token = create_access_token({"sub": user_id})
            auth_headers = {"Authorization": f"Bearer {token}"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Create a subject
            subj_data = {
                "name": "Computer Science",
                "description": "Introduction to programming and systems",
                "color": "#00ffcc",
                "icon": "Cpu",
                "difficulty": 4
            }
            response = await client.post("/api/subjects", json=subj_data, headers=auth_headers)
            assert response.status_code == 201, response.text
            subject = response.json()
            assert subject["name"] == "Computer Science"
            subj_id = subject["id"]

            # 2. List subjects
            response_list = await client.get("/api/subjects", headers=auth_headers)
            assert response_list.status_code == 200
            subjects = response_list.json()
            assert len(subjects) == 1
            assert subjects[0]["id"] == subj_id

            # 3. Update subject
            update_data = {
                "difficulty": 5,
                "mastery_score": 0.25
            }
            response_update = await client.put(f"/api/subjects/{subj_id}", json=update_data, headers=auth_headers)
            assert response_update.status_code == 200
            assert response_update.json()["difficulty"] == 5

            # 4. Create an exam
            exam_data = {
                "subject_id": subj_id,
                "title": "Midterm Exam",
                "exam_date": "2026-07-15",
                "importance": 4,
                "notes": "Covers chapters 1 to 5"
            }
            response_exam = await client.post("/api/exams", json=exam_data, headers=auth_headers)
            assert response_exam.status_code == 201
            exam = response_exam.json()
            exam_id = exam["id"]

            # 5. List exams
            response_exams_list = await client.get("/api/exams", headers=auth_headers)
            assert len(response_exams_list.json()) == 1

            # 6. Delete exam
            response_exam_delete = await client.delete(f"/api/exams/{exam_id}", headers=auth_headers)
            assert response_exam_delete.status_code == 204

            # 7. Delete subject
            response_subj_delete = await client.delete(f"/api/subjects/{subj_id}", headers=auth_headers)
            assert response_subj_delete.status_code == 204

        # Drop tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    try:
        asyncio.run(run_test())
    finally:
        app.dependency_overrides.clear()
