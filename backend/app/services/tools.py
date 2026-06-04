from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .security import assess_prompt


@dataclass
class Tool:
    name: str
    description: str
    handler: Callable[..., dict[str, Any]]
    allowed_args: set[str]
    requires_confirmation: bool = False


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self.register(
            Tool(
                name="create_ticket",
                description="Create a safe internal follow-up ticket.",
                handler=self._create_ticket,
                allowed_args={"title", "description"},
            )
        )
        self.register(
            Tool(
                name="risk_report",
                description="Assess prompt or content risk and return mitigation advice.",
                handler=self._risk_report,
                allowed_args={"text"},
            )
        )

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def call(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        if name not in self._tools:
            return {"ok": False, "error": f"tool_not_allowed:{name}"}
        tool = self._tools[name]
        extra_args = set(args) - tool.allowed_args
        if extra_args:
            return {"ok": False, "error": "invalid_tool_args", "extra_args": sorted(extra_args)}
        return {"ok": True, "tool": name, "result": tool.handler(**args)}

    @staticmethod
    def _create_ticket(title: str, description: str) -> dict[str, Any]:
        return {
            "ticket_id": "TICKET-DEMO-001",
            "title": title[:120],
            "description": description[:500],
            "status": "created",
        }

    @staticmethod
    def _risk_report(text: str) -> dict[str, Any]:
        assessment = assess_prompt(text)
        return {
            "risk_score": assessment.risk_score,
            "flags": assessment.flags,
            "allowed": assessment.allowed,
            "mitigations": [
                "use a tool allowlist",
                "validate tool parameters with schema",
                "redact sensitive fields before model calls",
                "require human confirmation for high-risk actions",
            ],
        }

