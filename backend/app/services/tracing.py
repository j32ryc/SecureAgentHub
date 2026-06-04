from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class TraceEvent:
    trace_id: str
    event_type: str
    message: str
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class TraceRecorder:
    def __init__(self) -> None:
        self._events: dict[str, list[TraceEvent]] = {}

    def new_trace(self) -> str:
        trace_id = str(uuid.uuid4())
        self._events[trace_id] = []
        return trace_id

    def record(self, trace_id: str, event_type: str, message: str, **metadata: object) -> TraceEvent:
        event = TraceEvent(trace_id=trace_id, event_type=event_type, message=message, metadata=dict(metadata))
        self._events.setdefault(trace_id, []).append(event)
        return event

    def get(self, trace_id: str) -> list[TraceEvent]:
        return self._events.get(trace_id, [])

