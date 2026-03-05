"""Pydantic output models used as ``output_type`` on SDK agents.

The ``PlanningResponse`` schema matches the JSON contract the frontend
expects (text + optional choices / provider_cards / free_text flags).
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Choice(BaseModel):
    emoji: str
    label: str
    desc: str = ""


class ProviderCardModel(BaseModel):
    emoji: str
    name: str
    location: str
    rating: float
    reviews: int
    price: int
    whatsSpecial: str
    buddiPick: bool = False


class PlanningResponse(BaseModel):
    """Structured output every planning agent must produce."""

    text: str
    choices: Optional[List[Choice]] = None
    multi_select: bool = False
    free_text: bool = False
    provider_cards: Optional[List[ProviderCardModel]] = None
