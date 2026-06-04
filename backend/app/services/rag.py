from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+")


@dataclass
class Document:
    doc_id: str
    title: str
    content: str


@dataclass
class SearchHit:
    doc_id: str
    title: str
    snippet: str
    score: float


class InMemoryDocumentStore:
    def __init__(self) -> None:
        self._docs: list[Document] = []

    def add(self, title: str, content: str) -> Document:
        doc = Document(doc_id=f"doc-{len(self._docs) + 1}", title=title, content=content)
        self._docs.append(doc)
        return doc

    def load_seed(self, seed_path: Path) -> None:
        if not seed_path.exists():
            return
        for item in json.loads(seed_path.read_text(encoding="utf-8")):
            self.add(item["title"], item["content"])

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        query_tokens = set(_tokenize(query))
        if not query_tokens:
            return []

        hits: list[SearchHit] = []
        for doc in self._docs:
            doc_tokens = _tokenize(f"{doc.title} {doc.content}")
            overlap = query_tokens.intersection(doc_tokens)
            if not overlap:
                continue
            score = len(overlap) / max(len(query_tokens), 1)
            hits.append(
                SearchHit(
                    doc_id=doc.doc_id,
                    title=doc.title,
                    snippet=_build_snippet(doc.content, overlap),
                    score=round(score, 3),
                )
            )
        return sorted(hits, key=lambda item: item.score, reverse=True)[:top_k]


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _build_snippet(content: str, overlap: set[str]) -> str:
    sentences = re.split(r"(?<=[。！？.!?])\s*", content)
    for sentence in sentences:
        lowered = sentence.lower()
        if any(token in lowered for token in overlap):
            return sentence[:220]
    return content[:220]

