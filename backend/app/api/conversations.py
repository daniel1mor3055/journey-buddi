from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.trip import Trip
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationRead,
    ConversationWithMessages,
    MessageCreate,
    MessageRead,
    PlanningStepResponse,
)
from app.agents.context import PlanningContext
from app.agents.orchestrator import orchestrator
from app.services.companion_chat import generate_companion_response
from app.services.tell_me_more_options import ACTIVE_TELL_ME_MORE

log = structlog.get_logger()
router = APIRouter(prefix="/conversations", tags=["conversations"])


def _msg_type_from(ai_response: dict) -> str:
    if ai_response.get("choices"):
        return "choices"
    if ai_response.get("provider_cards"):
        return "provider_cards"
    return "text"


def _response_metadata(ai_response: dict) -> dict:
    return {k: v for k, v in ai_response.items() if k != "text" and v is not None}


@router.post("", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: ConversationCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trip).where(Trip.id == body.trip_id, Trip.user_id == user.id)
    )
    trip = result.scalar_one_or_none()
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    memory = PlanningContext()
    conv = Conversation(
        trip_id=body.trip_id,
        user_id=user.id,
        title=body.title or "Planning Conversation",
        planning_step=memory.current_agent,
        planning_state=memory.to_dict(),
    )
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return conv


@router.get("", response_model=list)
async def list_conversations(
    trip_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.trip_id == trip_id, Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
    )
    convs = result.scalars().all()
    return [ConversationRead.model_validate(c) for c in convs]


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await _get_user_conversation(conversation_id, user.id, db)
    return conv


@router.post("/{conversation_id}/messages", response_model=PlanningStepResponse)
async def send_message(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await _get_user_conversation(conversation_id, user.id, db)

    max_order = max((m.sort_order for m in conv.messages), default=-1)

    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=body.content,
        message_type=body.message_type,
        metadata_=body.metadata or {},
        sort_order=max_order + 1,
    )
    db.add(user_msg)

    memory = PlanningContext.from_dict(conv.planning_state)

    if (
        memory.current_agent == "greeting"
        and body.content.strip().lower() == "tell me more first"
    ):
        ai_response: dict = {
            "text": ACTIVE_TELL_ME_MORE,
            "choices": [
                {"emoji": "🎯", "label": "Let's do it!", "desc": "Start planning your trip"},
            ],
        }
    else:
        history = [{"role": m.role, "content": m.content} for m in conv.messages]
        history.append({"role": "user", "content": body.content})

        ai_response, memory = await orchestrator.process_message(
            ctx=memory,
            user_message=body.content,
            conversation_history=history,
            conversation_id=str(conv.id),
        )

    conv.planning_state = memory.to_dict()
    conv.planning_step = memory.current_agent

    response_text = ai_response.get("text", "Let's continue!")

    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=response_text,
        message_type=_msg_type_from(ai_response),
        metadata_=_response_metadata(ai_response),
        sort_order=max_order + 2,
    )
    db.add(assistant_msg)

    await db.flush()

    return PlanningStepResponse(
        messages=[
            MessageRead.model_validate(user_msg),
            MessageRead.model_validate(assistant_msg),
        ],
        planning_step=conv.planning_step,
        planning_state=conv.planning_state,
        progress_percent=orchestrator.progress_percent(memory),
    )


@router.post("/{conversation_id}/init", response_model=PlanningStepResponse)
async def init_conversation(
    conversation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initialize a conversation with the greeting (no user message needed)."""
    conv = await _get_user_conversation(conversation_id, user.id, db)

    memory = PlanningContext.from_dict(conv.planning_state)

    if conv.messages:
        return PlanningStepResponse(
            messages=[MessageRead.model_validate(m) for m in conv.messages],
            planning_step=conv.planning_step,
            planning_state=conv.planning_state,
            progress_percent=orchestrator.progress_percent(memory),
        )

    ai_response, memory = await orchestrator.init_conversation(memory, conversation_id=str(conv.id))

    conv.planning_state = memory.to_dict()
    conv.planning_step = memory.current_agent

    response_text = ai_response.get("text", "Hey there! Let's plan your trip!")

    msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=response_text,
        message_type=_msg_type_from(ai_response),
        metadata_=_response_metadata(ai_response),
        sort_order=0,
    )
    db.add(msg)
    await db.flush()

    return PlanningStepResponse(
        messages=[MessageRead.model_validate(msg)],
        planning_step=conv.planning_step,
        planning_state=conv.planning_state,
        progress_percent=orchestrator.progress_percent(memory),
    )


@router.post("/{conversation_id}/back", response_model=PlanningStepResponse)
async def go_back(
    conversation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Go back to the previous agent in the pipeline."""
    conv = await _get_user_conversation(conversation_id, user.id, db)
    memory = PlanningContext.from_dict(conv.planning_state)

    if not memory.completed_agents:
        raise HTTPException(status_code=400, detail="Already at the first step")

    previous_agent_name = memory.completed_agents.pop()
    memory.current_agent = previous_agent_name

    ai_response, memory = await orchestrator.init_conversation(memory, conversation_id=str(conv.id))

    conv.planning_state = memory.to_dict()
    conv.planning_step = memory.current_agent

    response_text = ai_response.get("text", "Let's revisit this step.")

    max_order = max((m.sort_order for m in conv.messages), default=-1)
    msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=response_text,
        message_type=_msg_type_from(ai_response),
        metadata_=_response_metadata(ai_response),
        sort_order=max_order + 1,
    )
    db.add(msg)
    await db.flush()

    return PlanningStepResponse(
        messages=[MessageRead.model_validate(m) for m in conv.messages]
        + [MessageRead.model_validate(msg)],
        planning_step=conv.planning_step,
        planning_state=conv.planning_state,
        progress_percent=orchestrator.progress_percent(memory),
    )


@router.post("/{conversation_id}/companion", response_model=PlanningStepResponse)
async def companion_message(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await _get_user_conversation(conversation_id, user.id, db)

    trip_result = await db.execute(
        select(Trip).where(Trip.id == conv.trip_id)
    )
    trip = trip_result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    max_order = max((m.sort_order for m in conv.messages), default=-1)

    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=body.content,
        message_type="text",
        metadata_={},
        sort_order=max_order + 1,
    )
    db.add(user_msg)

    history = [
        {"role": m.role, "content": m.content}
        for m in conv.messages[-20:]
    ]
    history.append({"role": "user", "content": body.content})

    response_text = await generate_companion_response(
        db=db,
        trip=trip,
        user_message=body.content,
        conversation_history=history,
    )

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

    return PlanningStepResponse(
        messages=[
            MessageRead.model_validate(user_msg),
            MessageRead.model_validate(assistant_msg),
        ],
        planning_step=conv.planning_step,
        planning_state=conv.planning_state,
        progress_percent=100.0,
    )


async def _get_user_conversation(
    conversation_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession
) -> Conversation:
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv
