from contextlib import asynccontextmanager
import asyncio
import json
import uuid as uuid_mod

import structlog
from fastapi import FastAPI, Query, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.logging import setup_logging

settings = get_settings()
setup_logging(settings.environment)
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("starting_up", environment=settings.environment)
    yield
    log.info("shutting_down")


app = FastAPI(
    title="Journey Buddi API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.exception("unhandled_error", path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}


from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.trips import router as trips_router
from app.api.conversations import router as conversations_router
from app.api.attractions import router as attractions_router
from app.api.itinerary import router as itinerary_router
from app.api.conditions import router as conditions_router
from app.api.briefings import router as briefings_router
from app.api.swaps import router as swaps_router
from app.api.notifications import router as notifications_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(trips_router, prefix="/api/v1")
app.include_router(conversations_router, prefix="/api/v1")
app.include_router(attractions_router, prefix="/api/v1")
app.include_router(itinerary_router, prefix="/api/v1")
app.include_router(conditions_router, prefix="/api/v1")
app.include_router(briefings_router, prefix="/api/v1")
app.include_router(swaps_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")


@app.websocket("/api/v1/ws/chat/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(default=""),
):
    from app.auth import decode_access_token
    from app.database import get_db
    from app.models.user import User
    from app.models.conversation import Conversation, Message
    from app.models.trip import Trip
    from app.services.openai_client import openai_client as gemini_client
    from app.services.companion_chat import generate_companion_response
    from app.services.planning import generate_step_response, next_step, update_planning_state, progress_percent

    user_id = decode_access_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()

    try:
        async for db in get_db():
            result = await db.execute(
                select(User).where(User.id == uuid_mod.UUID(user_id))
            )
            user = result.scalar_one_or_none()
            if not user:
                await websocket.close(code=4001, reason="User not found")
                return

            conv_result = await db.execute(
                select(Conversation)
                .options(selectinload(Conversation.messages))
                .where(
                    Conversation.id == uuid_mod.UUID(conversation_id),
                    Conversation.user_id == user.id,
                )
            )
            conv = conv_result.scalar_one_or_none()
            if not conv:
                await websocket.close(code=4004, reason="Conversation not found")
                return

            trip_result = await db.execute(
                select(Trip).where(Trip.id == conv.trip_id)
            )
            trip = trip_result.scalar_one_or_none()

            while True:
                try:
                    raw = await asyncio.wait_for(websocket.receive_text(), timeout=300)
                except asyncio.TimeoutError:
                    await websocket.close(code=1000, reason="Idle timeout")
                    return

                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    data = {"type": "message", "content": raw}

                msg_type = data.get("type", "message")
                content = data.get("content", "")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue

                if not content:
                    continue

                max_order = max((m.sort_order for m in conv.messages), default=-1)

                user_msg = Message(
                    conversation_id=conv.id,
                    role="user",
                    content=content,
                    message_type="text",
                    metadata_={},
                    sort_order=max_order + 1,
                )
                db.add(user_msg)

                await websocket.send_json({"type": "stream_start"})

                is_companion = trip and trip.status == "active"
                history = [
                    {"role": m.role, "content": m.content}
                    for m in conv.messages[-20:]
                ]
                history.append({"role": "user", "content": content})

                if is_companion:
                    response_text = await generate_companion_response(
                        db=db, trip=trip, user_message=content,
                        conversation_history=history,
                    )
                    for i in range(0, len(response_text), 20):
                        chunk = response_text[i : i + 20]
                        await websocket.send_json({"type": "stream_token", "token": chunk})
                else:
                    conv.planning_state = update_planning_state(
                        conv.planning_state, conv.planning_step, content,
                    )
                    new_step = next_step(conv.planning_step)
                    if new_step:
                        conv.planning_step = new_step

                    ai_response = await generate_step_response(
                        step=conv.planning_step,
                        planning_state=conv.planning_state,
                        user_message=content,
                        conversation_history=history,
                    )
                    response_text = ai_response.get("text", "Let's continue!")

                    for i in range(0, len(response_text), 20):
                        chunk = response_text[i : i + 20]
                        await websocket.send_json({"type": "stream_token", "token": chunk})

                assistant_msg = Message(
                    conversation_id=conv.id,
                    role="assistant",
                    content=response_text,
                    message_type="text",
                    metadata_={},
                    sort_order=max_order + 2,
                )
                db.add(assistant_msg)
                await db.flush()

                await websocket.send_json({
                    "type": "stream_end",
                    "full_content": response_text,
                    "planning_step": conv.planning_step,
                    "progress_percent": progress_percent(conv.planning_step),
                })

    except WebSocketDisconnect:
        log.info("websocket_disconnected", conversation_id=conversation_id)
    except Exception:
        log.exception("websocket_error", conversation_id=conversation_id)
        try:
            await websocket.close(code=1011, reason="Internal error")
        except Exception:
            pass
