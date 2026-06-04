# Architecture

SecureAgentHub is built around a simple production-like Agent flow:

1. The frontend sends a user message through an SSE endpoint.
2. The backend creates a trace ID for the request.
3. The prompt risk guard checks injection and sensitive-data indicators.
4. The RAG retriever searches the enterprise knowledge base.
5. The Agent runtime decides whether to call an allowlisted tool.
6. The mock LLM streams a deterministic answer for offline demos.
7. Every step is recorded in the trace recorder.

## Components

### Prompt Risk Guard

The guard detects common prompt-injection patterns such as ignoring previous instructions, requesting system prompts, requesting secrets, and trying to reach internal metadata endpoints.

### RAG Store

The MVP uses an in-memory keyword retriever so the project can run without external services. The next production-oriented step is to replace it with Qdrant, Milvus, or pgvector.

### Tool Registry

Tools are not called freely. Each tool has a name, description, allowed argument list, and handler. Invalid tool names or extra arguments are rejected.

### Trace Recorder

The trace recorder saves security decisions, retrieved documents, tool results, and generated chunks. This makes Agent behavior explainable in interviews and easier to debug in real systems.

## Why This Matters

Enterprise Agent systems are not ordinary chatbots. Once an Agent can call tools, query business systems, or act on user intent, it becomes a new execution entry point. That requires permission design, audit logs, fallback behavior, and risk controls.

