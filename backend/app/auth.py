from datetime import datetime, timedelta
from typing import Optional
import hashlib
import hmac
import base64
import json
import threading

import jwt
from jwt import PyJWKClient

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.database import get_db
from app.models import User

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


def _hash_password(password: str) -> str:
    """Simple SHA-256 password hash (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hmac.compare_digest(_hash_password(password), hashed)


def hash_password(password: str) -> str:
    return _hash_password(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a simple HS256-like JWT (manual implementation, no PyJWT dep)."""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {**data, "exp": expire.isoformat()}
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(settings.JWT_SECRET.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


# ── JWKS-backed ES256 verifier ───────────────────────────────────────────────
# PyJWKClient fetches and caches Supabase's public keys automatically.
# lifespan_seconds=300 re-fetches keys every 5 minutes (handles key rotation).
_SUPABASE_JWKS_URL = f"{(settings.SUPABASE_URL or '').rstrip('/')}/auth/v1/.well-known/jwks.json"
_jwks_client: Optional[PyJWKClient] = None
_jwks_lock = threading.Lock()


def _get_jwks_client() -> Optional[PyJWKClient]:
    """Return a lazily-initialised, module-level PyJWKClient (thread-safe)."""
    global _jwks_client
    if _jwks_client is None and settings.SUPABASE_URL:
        with _jwks_lock:
            if _jwks_client is None:
                _jwks_client = PyJWKClient(
                    _SUPABASE_JWKS_URL,
                    lifespan=300,  # refresh keys every 5 minutes
                    headers={"User-Agent": "StudyMindAI-backend/1.0"},
                )
    return _jwks_client


def decode_access_token(token: str) -> Optional[dict]:
    """Verify a Supabase ES256 JWT via JWKS and return its payload, or None.
    Supports a 2-part mock token signature check as fallback for local testing.
    """
    try:
        parts = token.split(".")
        if len(parts) == 2:
            # Mock JWT for local tests
            payload_b64, sig = parts
            secret_bytes = settings.JWT_SECRET.encode()
            expected_sig = hmac.new(secret_bytes, payload_b64.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected_sig):
                return None
            payload_pad = payload_b64 + "=" * ((4 - len(payload_b64) % 4) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_pad).decode())
            exp_val = payload.get("exp")
            if exp_val:
                try:
                    exp_dt = datetime.fromisoformat(exp_val)
                    if datetime.utcnow() > exp_dt:
                        return None
                except ValueError:
                    import time
                    if time.time() > float(exp_val):
                        return None
            return payload
    except Exception as e:
        print(f"[Auth] Error decoding mock token: {e}")
        return None

    client = _get_jwks_client()
    if client is None:
        print("[Auth] SUPABASE_URL not configured — cannot verify JWT.")
        return None
    try:
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],  # accept both ECC and RSA keys
            options={"verify_aud": False},   # Supabase JWTs have no aud claim
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("[Auth] Token has expired.")
        return None
    except jwt.InvalidTokenError as exc:
        print(f"[Auth] Invalid token: {exc}")
        return None
    except Exception as exc:
        print(f"[Auth] Unexpected error verifying token: {exc}")
        return None
    


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate the Supabase JWT and return the corresponding User row.

    If the user row doesn't exist yet (Supabase trigger race condition on first
    login), it is created automatically from the JWT payload.
    """
    actual_token = credentials.credentials if credentials else token

    if not actual_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(actual_token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id: str = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        # Supabase trigger may not have run yet — upsert from JWT claims.
        email = payload.get("email") or ""
        meta = payload.get("user_metadata") or {}
        user = User(
            id=user_id,
            email=email,
            full_name=meta.get("full_name", ""),
            study_hours_per_day=int(meta.get("study_hours_per_day", 4)),
        )
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
        except Exception:
            await db.rollback()
            # Another request may have inserted it concurrently — try again.
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Like get_current_user but returns None instead of raising."""
    actual_token = None
    if credentials:
        actual_token = credentials.credentials
    elif token:
        actual_token = token

    if not actual_token:
        return None
    try:
        payload = decode_access_token(actual_token)
        if not payload or "sub" not in payload:
            return None
        result = await db.execute(select(User).where(User.id == payload["sub"]))
        return result.scalar_one_or_none()
    except Exception:
        return None

