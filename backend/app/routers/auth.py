"""Auth router — Supabase Auth integration.

Authentication (sign-up, login, password reset) is handled by Supabase Auth
on the frontend via the Supabase JS client.  The backend's only responsibility
is to:
  1. Verify the ES256 JWT issued by Supabase (done in app.auth.decode_access_token).
  2. Look up / lazily create the corresponding row in public.users.
  3. Return the user profile via GET /api/auth/me.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserOut
from app.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated Supabase user."""
    return UserOut.model_validate(user)
