from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.auth import create_access_token, create_magic_link_token, verify_magic_link_token
from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.redis import get_redis
from app.schemas.auth import (
    AuthResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    VerifyTokenRequest,
)

log = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/magic-link", response_model=MagicLinkResponse)
async def send_magic_link(body: MagicLinkRequest):
    token = create_magic_link_token(body.email)

    redis = await get_redis()
    await redis.setex(f"magic_link:{token}", settings.magic_link_expire_minutes * 60, body.email)

    magic_link_url = f"{settings.frontend_url}/auth/verify?token={token}"

    if settings.environment in ("development", "test"):
        log.info("magic_link_generated", email=body.email, url=magic_link_url)
    else:
        try:
            import resend

            resend.api_key = settings.resend_api_key
            resend.Emails.send(
                {
                    "from": settings.from_email,
                    "to": [body.email],
                    "subject": "Sign in to Journey Buddi",
                    "html": f"""
                    <h2>Welcome to Journey Buddi!</h2>
                    <p>Click the link below to sign in:</p>
                    <a href="{magic_link_url}" style="
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #2D9CDB;
                        color: white;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: 600;
                    ">Sign In</a>
                    <p style="color: #888; font-size: 12px; margin-top: 16px;">
                        This link expires in {settings.magic_link_expire_minutes} minutes.
                    </p>
                    """,
                }
            )
        except Exception:
            log.exception("failed_to_send_email", email=body.email)
            raise HTTPException(status_code=500, detail="Failed to send email")

    return MagicLinkResponse(expires_in=settings.magic_link_expire_minutes * 60)


@router.post("/verify", response_model=AuthResponse)
async def verify_magic_link(
    body: VerifyTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    redis = await get_redis()
    stored_email = await redis.get(f"magic_link:{body.token}")
    if stored_email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    email = verify_magic_link_token(body.token)
    if email is None or email != stored_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    await redis.delete(f"magic_link:{body.token}")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(email=email)
        db.add(user)
        await db.flush()

    user.last_login_at = datetime.now(timezone.utc)

    access_token = create_access_token(str(user.id))

    log.info("user_authenticated", user_id=str(user.id), email=email)

    return AuthResponse(
        access_token=access_token,
        user={"id": str(user.id), "email": user.email, "name": user.name},
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    user: User = Depends(get_current_user),
):
    access_token = create_access_token(str(user.id))
    return AuthResponse(
        access_token=access_token,
        user={"id": str(user.id), "email": user.email, "name": user.name},
    )


@router.post("/logout")
async def logout():
    return {"message": "Logged out"}
