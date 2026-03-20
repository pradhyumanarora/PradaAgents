import React, { useState, useEffect, useCallback } from 'react';
import TaskPanel from './components/TaskPanel';
import McpServersPanel from './components/McpServersPanel';
import AgentsPanel from './components/AgentsPanel';
import { fetchHistory, fetchTaskById, deleteChat } from './api';

const PAGES = {
  task: 'Run Task',
  mcp: 'MCP Servers',
  agents: 'Agents',
};

export default function App() {
  const [page, setPage] = useState('task');

  // Lifted task state — survives page navigation
  const [taskText, setTaskText] = useState('');
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState('idle');
  const [activeSessionId, setActiveSessionId] = useState(null);

  // Chat history
  const [history, setHistory] = useState([]);

  const loadHistory = useCallback(async () => {
    try {
      const data = await fetchHistory();
      setHistory(data.sessions || []);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  // Reload history when a task completes or errors
  useEffect(() => {
    if (status === 'completed' || status === 'error') loadHistory();
  }, [status, loadHistory]);

  async function handleLoadSession(id) {
    try {
      const data = await fetchTaskById(id);
      setTaskText(data.task || '');
      setMessages(data.messages || []);
      setStatus(data.status === 'running' ? 'running' : data.status === 'stopped' ? 'stopped' : data.status === 'error' ? 'error' : 'completed');
      setActiveSessionId(id);
      setPage('task');
    } catch { /* ignore */ }
  }

  async function handleDeleteChat(e, id) {
    e.stopPropagation();
    try {
      await deleteChat(id);
      if (activeSessionId === id) handleNewChat();
      await loadHistory();
    } catch { /* ignore */ }
  }

  function handleNewChat() {
    setTaskText('');
    setMessages([]);
    setStatus('idle');
    setActiveSessionId(null);
    setPage('task');
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <nav className="sidebar">
        <h2>⚡ PradaAgent</h2>

        <div>
          <h3>Navigation</h3>
          {Object.entries(PAGES).map(([key, label]) => (
            <button
              key={key}
              className={`nav-btn ${page === key ? 'active' : ''}`}
              onClick={() => setPage(key)}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Chat History */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Chat History</h3>
            <button className="btn-secondary" onClick={handleNewChat}
              style={{ padding: '3px 8px', fontSize: '0.72rem' }}>+ New</button>
          </div>
          <div className="history-list">
            {history.length === 0 ? (
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>No chats yet</p>
            ) : (
              history.map((s) => (
                <div key={s.id} className={`history-item ${activeSessionId === s.id ? 'active' : ''}`}>
                  <button className="history-item-btn" onClick={() => handleLoadSession(s.id)}>
                    <span className={`history-status ${s.status}`} />
                    <span className="history-task">{s.task}</span>
                  </button>
                  <button className="history-delete" onClick={(e) => handleDeleteChat(e, s.id)} title="Delete chat">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div style={{ marginTop: 'auto', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          Agentic Development Team v1.1
        </div>
      </nav>

      {/* Main content */}
      <div className="main">
        <header className="header">
          <h1>{PAGES[page]}</h1>
        </header>

        <div className="content">
          {page === 'task' && (
            <TaskPanel
              taskText={taskText} setTaskText={setTaskText}
              messages={messages} setMessages={setMessages}
              status={status} setStatus={setStatus}
              activeSessionId={activeSessionId}
              setActiveSessionId={setActiveSessionId}
            />
          )}
          {page === 'mcp' && <McpServersPanel />}
          {page === 'agents' && <AgentsPanel />}
        </div>
      </div>
    </div>
  );
}
