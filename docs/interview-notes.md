# Interview Notes

## 60-second project pitch

SecureAgentHub is an enterprise AI Agent demo built with FastAPI. It supports streaming chat, RAG retrieval, controlled Tool Calling, prompt-injection checks, sensitive-data redaction, and execution trace logs. I built it to show how AI Agent applications should be engineered for enterprise use, especially when they connect to knowledge bases and business tools.

My security background helps here because Agent systems introduce new permission boundaries. The model can generate intent, but tools must still be controlled by allowlists, schema validation, audit logs, and fallback strategies.

## RAG explanation

RAG improves answers by retrieving external knowledge before generation. In production, the difficult parts are document chunking, retrieval quality, reranking, citation, evaluation, and hallucination control. If RAG answers incorrectly, I would inspect whether the right chunks were retrieved, whether the context was too noisy, and whether the final prompt forced the model to answer only from retrieved evidence.

## Tool Calling explanation

I do not let the Agent freely execute arbitrary tools. Tools are registered in an allowlist, arguments are validated, and sensitive or high-risk actions require human confirmation. Every tool call is recorded with input, output, latency, and error information.

## Prompt Injection explanation

Prompt Injection is treated as untrusted input. The system checks for attempts to ignore system instructions, reveal hidden prompts, request secrets, or force unsafe tool usage. Detection alone is not enough, so the stronger defense is tool isolation and strict permission control.

## Why my security background is useful

I have long-term experience in red team and penetration testing. That trained me to analyze permission boundaries, abnormal inputs, chain risks, and system weak points. In AI Agent engineering, those skills map directly to tool-calling safety, data access control, auditability, and failure recovery.

