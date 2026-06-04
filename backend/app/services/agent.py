from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .llm import MockLLM
from .rag import InMemoryDocumentStore
from .security import assess_prompt
from .tools import ToolRegistry
from .tracing import TraceRecorder


class SecureAgent:
    def __init__(self) -> None:
        self.docs = InMemoryDocumentStore()
        self.docs.load_seed(Path(__file__).resolve().parents[1] / "data" / "seed_docs.json")
        self.tools = ToolRegistry()
        self.traces = TraceRecorder()
        self.llm = MockLLM()

    def stream(self, message: str, session_id: str) -> Iterator[dict[str, Any]]:
        trace_id = self.traces.new_trace()
        self.traces.record(trace_id, "session", "chat_started", session_id=session_id)
        yield {"type": "trace", "trace_id": trace_id}

        assessment = assess_prompt(message)
        self.traces.record(
            trace_id,
            "security",
            "prompt_assessed",
            risk_score=assessment.risk_score,
            flags=assessment.flags,
        )
        yield {
            "type": "security",
            "risk_score": assessment.risk_score,
            "flags": assessment.flags,
            "allowed": assessment.allowed,
        }

        if not assessment.allowed:
            self.traces.record(trace_id, "blocked", "blocked_high_risk_prompt")
            yield {
                "type": "delta",
                "text": "检测到高风险提示词注入或敏感操作请求，本次不会继续调用工具。请改写为授权范围内的业务问题。",
            }
            yield {"type": "done", "trace_id": trace_id}
            return

        hits = self.docs.search(assessment.sanitized_text)
        self.traces.record(
            trace_id,
            "rag",
            "knowledge_retrieved",
            hits=[hit.__dict__ for hit in hits],
        )
        yield {"type": "rag", "hits": [hit.__dict__ for hit in hits]}

        tool_result = self._maybe_call_tool(assessment.sanitized_text)
        if tool_result:
            self.traces.record(trace_id, "tool", "tool_called", result=tool_result)
            yield {"type": "tool", "result": tool_result}

        for chunk in self.llm.stream_answer(assessment.sanitized_text, hits, tool_result):
            self.traces.record(trace_id, "llm", "chunk_generated", chars=len(chunk))
            yield {"type": "delta", "text": chunk}

        self.traces.record(trace_id, "session", "chat_completed")
        yield {"type": "done", "trace_id": trace_id}

    def add_document(self, title: str, content: str) -> dict[str, str]:
        doc = self.docs.add(title, content)
        return {"doc_id": doc.doc_id, "title": doc.title}

    def get_trace(self, trace_id: str) -> list[dict[str, Any]]:
        return [event.__dict__ for event in self.traces.get(trace_id)]

    def _maybe_call_tool(self, message: str) -> dict[str, Any] | None:
        if any(keyword in message for keyword in ["风险", "注入", "脱敏", "越权", "权限"]):
            return self.tools.call("risk_report", {"text": message})
        if any(keyword in message.lower() for keyword in ["bug", "工单", "ticket", "故障"]):
            return self.tools.call(
                "create_ticket",
                {
                    "title": "Agent generated follow-up",
                    "description": message,
                },
            )
        return None

