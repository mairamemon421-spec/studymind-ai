import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.auth import create_access_token

def test_auth_flow():
    # Setup isolated test database engine
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
                email="testuser@example.com",
                full_name="Test User",
                study_hours_per_day=4,
            )
            db.add(user)
            await db.commit()

            # 2. Generate a mock token
            token = create_access_token({"sub": user_id})

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 3. Access protected route with correct token
            headers = {"Authorization": f"Bearer {token}"}
            response_me = await client.get("/api/auth/me", headers=headers)
            assert response_me.status_code == 200
            data = response_me.json()
            assert data["email"] == "testuser@example.com"
            assert data["full_name"] == "Test User"

            # 4. Access protected route with invalid token
            headers_bad = {"Authorization": "Bearer bad-token"}
            response_bad = await client.get("/api/auth/me", headers=headers_bad)
            assert response_bad.status_code == 401

            # 5. Access protected route without token
            response_no_token = await client.get("/api/auth/me")
            assert response_no_token.status_code == 401

        # Drop tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    try:
        asyncio.run(run_test())
    finally:
        app.dependency_overrides.clear()
