from __future__ import annotations

from collections.abc import Iterable

from .rag import SearchHit


class MockLLM:
    """A deterministic local model substitute for demos and interviews."""

    def stream_answer(self, message: str, hits: list[SearchHit], tool_result: dict | None) -> Iterable[str]:
        yield "我会按企业级 Agent 的方式处理这个问题：先判断风险，再检索知识库，必要时调用受控工具。"
        if hits:
            titles = "、".join(hit.title for hit in hits)
            yield f" 当前检索到的相关知识包括：{titles}。"
        else:
            yield " 当前知识库没有强相关资料，需要补充文档或转人工确认。"
        if tool_result:
            yield f" 工具调用结果：{tool_result.get('result', tool_result)}。"
        yield f" 针对你的问题「{message[:80]}」，建议输出带引用、带审计记录，并对高风险动作设置人工确认。"

