import React, { useState, useEffect } from 'react';
import { fetchAgents } from '../api';

export default function AgentsPanel() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgents()
      .then((data) => setAgents(data.agents || []))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p><span className="spinner" /> Loading agents…</p>;
  }

  return (
    <div className="agents-grid">
      {agents.map((a) => (
        <div key={a.name} className="agent-card">
          <h4>{a.name}</h4>
          <p>{a.description}</p>
          <div className="agent-mcp-list">
            {a.mcp_servers.length === 0 ? (
              <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>No MCP servers mapped</span>
            ) : (
              a.mcp_servers.map((s) => (
                <span key={s} className="type-badge http">{s}</span>
              ))
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
