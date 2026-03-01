from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()
router = APIRouter(prefix="/notifications", tags=["notifications"])


class PushSubscriptionCreate(BaseModel):
    endpoint: str
    p256dh_key: str
    auth_key: str
    user_agent: str = ""


@router.post("/subscribe")
async def subscribe_push(
    body: PushSubscriptionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(PushSubscription).where(
            PushSubscription.user_id == user.id,
            PushSubscription.endpoint == body.endpoint,
        )
    )
    sub = existing.scalar_one_or_none()

    if sub:
        sub.p256dh_key = body.p256dh_key
        sub.auth_key = body.auth_key
        sub.is_active = True
    else:
        sub = PushSubscription(
            user_id=user.id,
            endpoint=body.endpoint,
            p256dh_key=body.p256dh_key,
            auth_key=body.auth_key,
            user_agent=body.user_agent,
        )
        db.add(sub)

    await db.flush()
    return {"status": "subscribed"}


@router.post("/unsubscribe")
async def unsubscribe_push(
    body: PushSubscriptionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PushSubscription).where(
            PushSubscription.user_id == user.id,
            PushSubscription.endpoint == body.endpoint,
        )
    )
    sub = result.scalar_one_or_none()
    if sub:
        sub.is_active = False
    return {"status": "unsubscribed"}


@router.get("/vapid-key")
async def get_vapid_key():
    return {"public_key": settings.vapid_public_key}
