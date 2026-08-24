from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Risk(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TicketRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=5000)
    channel: str = Field("web", pattern="^(web|chat|email|mobile)$")


class Classification(BaseModel):
    topic: str
    risk: Risk
    reasons: list[str]
    confidence: float


class TicketResult(BaseModel):
    ticket_id: str
    status: str
    classification: Classification
    answer: Optional[str] = None
    knowledge_article: Optional[str] = None
    answer_source: Optional[str] = None
    operator_queue: Optional[str] = None
    routing_ms: float
    total_ms: float
    created_at: str

