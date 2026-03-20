import React, { useState } from 'react';
import TaskPanel from './components/TaskPanel';
import McpServersPanel from './components/McpServersPanel';
import AgentsPanel from './components/AgentsPanel';

const PAGES = {
  task: 'Run Task',
  mcp: 'MCP Servers',
  agents: 'Agents',
};

export default function App() {
  const [page, setPage] = useState('task');

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

        <div style={{ marginTop: 'auto', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          Agentic Development Team v1.0
        </div>
      </nav>

      {/* Main content */}
      <div className="main">
        <header className="header">
          <h1>{PAGES[page]}</h1>
        </header>

        <div className="content">
          {page === 'task' && <TaskPanel />}
          {page === 'mcp' && <McpServersPanel />}
          {page === 'agents' && <AgentsPanel />}
        </div>
      </div>
    </div>
  );
}
