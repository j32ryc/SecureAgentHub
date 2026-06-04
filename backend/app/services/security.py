from __future__ import annotations

import re
from dataclasses import dataclass, field


PROMPT_INJECTION_PATTERNS = {
    "ignore_previous": re.compile(r"(ignore|忽略|无视).{0,20}(previous|system|developer|之前|系统|开发者)", re.I),
    "reveal_prompt": re.compile(r"(system prompt|系统提示词|开发者消息|隐藏指令|prompt泄露|提示词泄露)", re.I),
    "secret_request": re.compile(r"(api[_ -]?key|token|secret|password|凭证|密钥|密码)", re.I),
    "unsafe_network": re.compile(r"(169\.254\.169\.254|metadata\.google|localhost|127\.0\.0\.1|内网地址)", re.I),
    "tool_escape": re.compile(r"(执行命令|反弹shell|下载并运行|bypass|越权|提权)", re.I),
}

SENSITIVE_PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{12,})"), r"\1=[REDACTED]"),
    (re.compile(r"\b1[3-9]\d{9}\b"), "[PHONE_REDACTED]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL_REDACTED]"),
    (re.compile(r"\b\d{17}[\dXx]\b"), "[ID_REDACTED]"),
]


@dataclass
class SecurityAssessment:
    allowed: bool
    risk_score: int
    flags: list[str] = field(default_factory=list)
    sanitized_text: str = ""


def redact_sensitive(text: str) -> str:
    redacted = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def assess_prompt(text: str) -> SecurityAssessment:
    flags: list[str] = []
    for name, pattern in PROMPT_INJECTION_PATTERNS.items():
        if pattern.search(text):
            flags.append(name)

    risk_score = min(100, len(flags) * 25)
    sanitized = redact_sensitive(text)
    return SecurityAssessment(
        allowed=risk_score < 75,
        risk_score=risk_score,
        flags=flags,
        sanitized_text=sanitized,
    )

