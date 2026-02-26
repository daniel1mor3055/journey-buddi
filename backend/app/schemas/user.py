from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserRead(BaseModel):
    id: UUID
    email: str
    name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    preferences: dict = {}
    profile: dict = {}

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    preferences: Optional[dict] = None
    profile: Optional[dict] = None
