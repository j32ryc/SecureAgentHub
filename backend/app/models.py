from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(default="demo-session", max_length=80)


class DocumentIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    content: str = Field(..., min_length=1, max_length=20000)


class TraceEventOut(BaseModel):
    trace_id: str
    event_type: str
    message: str
    metadata: dict

