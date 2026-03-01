from __future__ import annotations

import json
from typing import Optional

import structlog
from pywebpush import webpush, WebPushException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.push_subscription import PushSubscription

log = structlog.get_logger()
settings = get_settings()


async def send_push_notification(
    db: AsyncSession,
    user_id: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
    tag: Optional[str] = None,
) -> int:
    result = await db.execute(
        select(PushSubscription).where(
            PushSubscription.user_id == user_id,
            PushSubscription.is_active == True,
        )
    )
    subscriptions = result.scalars().all()

    if not subscriptions:
        log.info("no_push_subscriptions", user_id=user_id)
        return 0

    payload = json.dumps({
        "title": title,
        "body": body,
        "icon": "/icons/buddi-192.png",
        "badge": "/icons/buddi-badge-72.png",
        "data": data or {},
        "tag": tag,
    })

    sent = 0
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh_key,
                        "auth": sub.auth_key,
                    },
                },
                data=payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_claims_email},
            )
            sent += 1
        except WebPushException as e:
            if e.response and e.response.status_code in (404, 410):
                sub.is_active = False
                log.info("push_subscription_expired", subscription_id=str(sub.id))
            else:
                log.warning("push_send_failed", error=str(e), subscription_id=str(sub.id))
        except Exception as e:
            log.warning("push_send_error", error=str(e))

    return sent


async def send_morning_briefing_notification(
    db: AsyncSession,
    user_id: str,
    trip_id: str,
    day_number: int,
    overall_assessment: str,
    summary: str,
):
    assessment_emoji = {
        "EXCELLENT": "🟢", "GOOD": "🟢", "FAIR": "🟡", "POOR": "🟠", "UNSAFE": "🔴",
    }
    emoji = assessment_emoji.get(overall_assessment, "📍")

    await send_push_notification(
        db=db,
        user_id=user_id,
        title=f"{emoji} Good morning! Day {day_number} briefing",
        body=summary[:120],
        data={"type": "briefing", "trip_id": trip_id, "day_number": day_number},
        tag=f"briefing-{trip_id}-{day_number}",
    )


async def send_swap_notification(
    db: AsyncSession,
    user_id: str,
    trip_id: str,
    swap_id: str,
    reason: str,
):
    await send_push_notification(
        db=db,
        user_id=user_id,
        title="💡 Itinerary improvement available",
        body=reason[:120],
        data={"type": "swap", "trip_id": trip_id, "swap_id": swap_id},
        tag=f"swap-{swap_id}",
    )


async def send_condition_alert(
    db: AsyncSession,
    user_id: str,
    trip_id: str,
    day_number: int,
    message: str,
):
    await send_push_notification(
        db=db,
        user_id=user_id,
        title="⚠️ Conditions have changed",
        body=message[:120],
        data={"type": "condition_alert", "trip_id": trip_id, "day_number": day_number},
        tag=f"alert-{trip_id}-{day_number}",
    )
