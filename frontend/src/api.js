const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchAgents() {
  const res = await fetch(`${API_BASE}/agents`);
  return res.json();
}

// ---- MCP Servers ----

export async function fetchMcpServers() {
  const res = await fetch(`${API_BASE}/mcp-servers`);
  return res.json();
}

export async function addMcpServer(server) {
  const res = await fetch(`${API_BASE}/mcp-servers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(server),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to add server');
  }
  return res.json();
}

export async function updateMcpServer(name, server) {
  const res = await fetch(`${API_BASE}/mcp-servers/${encodeURIComponent(name)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(server),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to update server');
  }
  return res.json();
}

export async function deleteMcpServer(name) {
  const res = await fetch(`${API_BASE}/mcp-servers/${encodeURIComponent(name)}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to delete server');
  }
  return res.json();
}

// ---- History ----

export async function fetchHistory() {
  const res = await fetch(`${API_BASE}/history`);
  return res.json();
}

export async function fetchTaskById(sessionId) {
  const res = await fetch(`${API_BASE}/tasks/${sessionId}`);
  if (!res.ok) throw new Error('Session not found');
  return res.json();
}

// ---- Model config ----

export async function fetchModelConfig() {
  const res = await fetch(`${API_BASE}/model-config`);
  return res.json();
}

// ---- Tasks ----

export async function createTask(task, modelName = 'gpt-4o', maxIterations = 30, azureEndpoint = '', azureApiVersion = '2025-04-01-preview') {
  const body = {
    task,
    model_name: modelName,
    max_iterations: maxIterations,
  };
  if (azureEndpoint) {
    body.azure_endpoint = azureEndpoint;
    body.azure_api_version = azureApiVersion;
  }
  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

export function streamTask(sessionId, onMessage, onDone, onError) {
  const evtSource = new EventSource(`${API_BASE}/tasks/${sessionId}/stream`);

  evtSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'done') {
        onDone(data);
        evtSource.close();
      } else if (data.type === 'error') {
        onError(data);
        evtSource.close();
      } else {
        onMessage(data);
      }
    } catch {
      // ignore parse errors
    }
  };

  evtSource.onerror = () => {
    onError({ content: 'Connection lost' });
    evtSource.close();
  };

  return evtSource; // caller can call .close() to stop
}

export async function stopTask(sessionId) {
  const res = await fetch(`${API_BASE}/tasks/${sessionId}/stop`, { method: 'POST' });
  return res.json();
}

export async function followUpTask(sessionId, prompt) {
  const res = await fetch(`${API_BASE}/tasks/${sessionId}/followup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to follow up');
  }
  return res.json();
}
