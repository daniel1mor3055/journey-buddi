from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str
    message_type: str = "text"
    metadata: Optional[dict] = None


class MessageRead(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    message_type: str
    metadata_: dict = {}
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    trip_id: UUID
    title: Optional[str] = None


class ConversationRead(BaseModel):
    id: UUID
    trip_id: UUID
    user_id: UUID
    title: Optional[str] = None
    planning_step: str
    planning_state: dict = {}
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationWithMessages(ConversationRead):
    messages: List[MessageRead] = []


class PlanningStepResponse(BaseModel):
    messages: List[MessageRead]
    planning_step: str
    planning_state: dict
    progress_percent: float
