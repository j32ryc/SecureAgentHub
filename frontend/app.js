const API_BASE = "http://localhost:8000";

const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const messages = document.querySelector("#messages");
const statusEl = document.querySelector("#status");
const traceList = document.querySelector("#trace-list");
const ragList = document.querySelector("#rag-list");
const securityBox = document.querySelector("#security-box");

let currentAgentMessage = null;

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error("bad status");
    statusEl.textContent = "API 已连接";
    statusEl.classList.add("ok");
  } catch {
    statusEl.textContent = "API 未连接";
    statusEl.classList.remove("ok");
  }
}

function addMessage(role, text = "") {
  const node = document.createElement("div");
  node.className = `message ${role}`;
  node.textContent = text;
  messages.appendChild(node);
  messages.scrollTop = messages.scrollHeight;
  return node;
}

function addTrace(eventType, message) {
  const item = document.createElement("div");
  item.className = "trace-item";
  item.innerHTML = `<strong>${eventType}</strong><span>${message}</span>`;
  traceList.prepend(item);
}

function renderRag(hits) {
  ragList.innerHTML = "";
  if (!hits.length) {
    ragList.textContent = "没有命中知识库";
    return;
  }
  for (const hit of hits) {
    const item = document.createElement("div");
    item.className = "rag-item";
    item.innerHTML = `<strong>${hit.title} · score ${hit.score}</strong><span>${hit.snippet}</span>`;
    ragList.appendChild(item);
  }
}

function renderSecurity(event) {
  securityBox.className = "security-box";
  if (event.risk_score >= 75) {
    securityBox.classList.add("block");
  } else if (event.risk_score > 0) {
    securityBox.classList.add("warn");
  } else {
    securityBox.classList.add("safe");
  }
  securityBox.textContent = `risk=${event.risk_score}; flags=${event.flags.length ? event.flags.join(", ") : "none"}`;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage("user", message);
  currentAgentMessage = addMessage("agent", "");
  input.value = "";
  form.querySelector("button").disabled = true;
  traceList.innerHTML = "";
  ragList.innerHTML = "";

  const url = `${API_BASE}/api/chat/stream?message=${encodeURIComponent(message)}&session_id=web-demo`;
  const stream = new EventSource(url);

  stream.addEventListener("trace", (evt) => {
    const data = JSON.parse(evt.data);
    addTrace("trace", data.trace_id);
  });

  stream.addEventListener("security", (evt) => {
    const data = JSON.parse(evt.data);
    renderSecurity(data);
    addTrace("security", `risk=${data.risk_score}`);
  });

  stream.addEventListener("rag", (evt) => {
    const data = JSON.parse(evt.data);
    renderRag(data.hits);
    addTrace("rag", `${data.hits.length} hits`);
  });

  stream.addEventListener("tool", (evt) => {
    const data = JSON.parse(evt.data);
    addTrace("tool", data.result.tool || "tool_called");
  });

  stream.addEventListener("delta", (evt) => {
    const data = JSON.parse(evt.data);
    currentAgentMessage.textContent += data.text;
    messages.scrollTop = messages.scrollHeight;
  });

  stream.addEventListener("done", (evt) => {
    const data = JSON.parse(evt.data);
    addTrace("done", data.trace_id);
    stream.close();
    form.querySelector("button").disabled = false;
  });

  stream.onerror = () => {
    addTrace("error", "stream closed or API unavailable");
    stream.close();
    form.querySelector("button").disabled = false;
  };
});

checkHealth();
setInterval(checkHealth, 5000);

