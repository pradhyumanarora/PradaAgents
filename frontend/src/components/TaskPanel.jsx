import React, { useState, useRef, useEffect } from 'react';
import { createTask, streamTask, fetchModelConfig } from '../api';

const AGENT_CLASS_MAP = {
  ArchitectAgent: 'architect',
  DeveloperAgent: 'developer',
  CodeReviewerAgent: 'reviewer',
  SecurityAgent: 'security',
  PRReviewAgent: 'pr',
  system: 'system',
};

function agentClass(source) {
  return AGENT_CLASS_MAP[source] || 'system';
}

export default function TaskPanel({ taskText, setTaskText, messages, setMessages, status, setStatus, setActiveSessionId }) {
  const [model, setModel] = useState('');
  const [maxIter, setMaxIter] = useState(30);
  const [modelCfg, setModelCfg] = useState(null);
  const bottomRef = useRef(null);

  // Fetch backend model config on mount
  useEffect(() => {
    fetchModelConfig().then((cfg) => {
      setModelCfg(cfg);
      if (cfg.default_model && !model) setModel(cfg.default_model);
    });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleRun() {
    if (!taskText.trim() || status === 'running') return;

    setMessages([]);
    setStatus('running');

    try {
      const azureEp = modelCfg?.is_azure ? modelCfg.azure_endpoint : '';
      const azureVer = modelCfg?.azure_api_version || '2024-12-01-preview';
      const { session_id } = await createTask(taskText, model, maxIter, azureEp, azureVer);
      setActiveSessionId(session_id);
      streamTask(
        session_id,
        (msg) => setMessages((prev) => [...prev, msg]),
        () => setStatus('completed'),
        (err) => {
          setMessages((prev) => [...prev, { source: 'system', content: err.content || 'Error', type: 'error' }]);
          setStatus('error');
        }
      );
    } catch {
      setStatus('error');
    }
  }

  return (
    <div>
      {/* Azure OpenAI banner */}
      {modelCfg?.is_azure && (
        <div className="card" style={{ borderLeft: '3px solid var(--agent-architect)', padding: '14px 18px' }}>
          <strong style={{ color: 'var(--agent-architect)' }}>Azure OpenAI</strong>
          <span style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginLeft: 12 }}>
            Endpoint: <code style={{ color: 'var(--text)' }}>{modelCfg.azure_endpoint}</code>
            &nbsp;|&nbsp;API version: <code style={{ color: 'var(--text)' }}>{modelCfg.azure_api_version}</code>
          </span>
        </div>
      )}

      {/* Task input */}
      <div className="card">
        <h3>Describe Your Task</h3>
        <div className="task-input-area">
          <textarea
            placeholder={`Example:\n1. ArchitectAgent: Design a REST API for user management\n2. DeveloperAgent: Implement with FastAPI\n3. SecurityAgent: Audit for OWASP Top 10\n4. CodeReviewerAgent: Final quality review\n\nWhen complete, respond with TASK_COMPLETE.`}
            value={taskText}
            onChange={(e) => setTaskText(e.target.value)}
            disabled={status === 'running'}
          />
          <div className="task-controls">
            <input
              placeholder="Model / Deployment name"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              disabled={status === 'running'}
              style={{ width: 180 }}
            />
            <label style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Max&nbsp;Iterations:&nbsp;
              <input
                type="number"
                min={1}
                max={100}
                value={maxIter}
                onChange={(e) => setMaxIter(Number(e.target.value))}
                style={{ width: 60 }}
                disabled={status === 'running'}
              />
            </label>
            <button className="btn-primary" onClick={handleRun} disabled={!taskText.trim() || status === 'running'}>
              {status === 'running' ? <><span className="spinner" /> Running…</> : 'Run Task'}
            </button>
            {status !== 'idle' && (
              <span className={`status ${status}`}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      {messages.length > 0 && (
        <div className="card">
          <h3>Agent Conversation ({messages.length} messages)</h3>
          <div className="messages-container">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.type === 'error' ? 'error' : agentClass(msg.source)}`}>
                <div className="message-header">
                  <span className={`agent-badge ${agentClass(msg.source)}`}>
                    {msg.source}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                    {msg.type}
                  </span>
                </div>
                <div className="message-content">{msg.content}</div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </div>
      )}
    </div>
  );
}
