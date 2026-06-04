from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .models import ChatRequest, DocumentIn
from .services.agent import SecureAgent

app = FastAPI(title="SecureAgentHub", version="0.1.0")
agent = SecureAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "secure-agent-hub"}


@app.post("/api/documents")
def add_document(document: DocumentIn) -> dict[str, str]:
    return agent.add_document(document.title, document.content)


@app.post("/api/chat")
def chat_once(request: ChatRequest) -> dict[str, object]:
    events = list(agent.stream(request.message, request.session_id))
    return {"events": events}


@app.get("/api/chat/stream")
def chat_stream(
    message: str = Query(..., min_length=1, max_length=4000),
    session_id: str = Query(default="demo-session", max_length=80),
) -> StreamingResponse:
    return StreamingResponse(_to_sse(agent.stream(message, session_id)), media_type="text/event-stream")


@app.get("/api/traces/{trace_id}")
def get_trace(trace_id: str) -> dict[str, object]:
    return {"trace_id": trace_id, "events": agent.get_trace(trace_id)}


def _to_sse(events: Iterator[dict[str, object]]) -> Iterator[str]:
    for event in events:
        event_type = str(event.get("type", "message"))
        payload = json.dumps(event, ensure_ascii=False)
        yield f"event: {event_type}\ndata: {payload}\n\n"

