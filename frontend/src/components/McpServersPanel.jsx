import React, { useState, useEffect, useCallback } from 'react';
import { fetchMcpServers, addMcpServer, deleteMcpServer } from '../api';

export default function McpServersPanel() {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', server_type: 'http', url: '', command: '', args: '' });

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchMcpServers();
      setServers(data.servers || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleAdd(e) {
    e.preventDefault();
    setError(null);
    try {
      const payload = {
        name: form.name,
        server_type: form.server_type,
      };
      if (form.server_type === 'http') {
        payload.url = form.url;
      } else {
        payload.command = form.command;
        payload.args = form.args
          ? form.args.split(',').map((s) => s.trim()).filter(Boolean)
          : [];
      }
      await addMcpServer(payload);
      setForm({ name: '', server_type: 'http', url: '', command: '', args: '' });
      setShowForm(false);
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleDelete(name) {
    if (!window.confirm(`Delete MCP server "${name}"?`)) return;
    try {
      await deleteMcpServer(name);
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>Configured MCP Servers</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn-secondary" onClick={load} disabled={loading}>
              Refresh
            </button>
            <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
              {showForm ? 'Cancel' : '+ Add Server'}
            </button>
          </div>
        </div>

        {error && <p style={{ color: 'var(--error)', marginTop: 8, fontSize: '0.85rem' }}>{error}</p>}

        {/* Add form */}
        {showForm && (
          <form className="add-server-form" onSubmit={handleAdd}>
            <input
              placeholder="Server name (e.g. github)"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
            <select
              value={form.server_type}
              onChange={(e) => setForm({ ...form, server_type: e.target.value })}
            >
              <option value="http">HTTP</option>
              <option value="stdio">stdio</option>
            </select>

            {form.server_type === 'http' ? (
              <input
                className="full-width"
                placeholder="URL (e.g. https://api.example.com/mcp)"
                value={form.url}
                onChange={(e) => setForm({ ...form, url: e.target.value })}
                required
              />
            ) : (
              <>
                <input
                  placeholder="Command (e.g. npx)"
                  value={form.command}
                  onChange={(e) => setForm({ ...form, command: e.target.value })}
                  required
                />
                <input
                  placeholder="Args (comma-separated)"
                  value={form.args}
                  onChange={(e) => setForm({ ...form, args: e.target.value })}
                />
              </>
            )}

            <button type="submit" className="btn-primary full-width">
              Add Server
            </button>
          </form>
        )}

        {/* Table */}
        {loading ? (
          <p style={{ marginTop: 16, color: 'var(--text-secondary)' }}><span className="spinner" /> Loading…</p>
        ) : servers.length === 0 ? (
          <p style={{ marginTop: 16, color: 'var(--text-secondary)' }}>No MCP servers configured yet.</p>
        ) : (
          <table className="mcp-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Endpoint / Command</th>
                <th style={{ width: 80 }}></th>
              </tr>
            </thead>
            <tbody>
              {servers.map((s) => (
                <tr key={s.name}>
                  <td style={{ fontWeight: 600 }}>{s.name}</td>
                  <td>
                    <span className={`type-badge ${s.type}`}>{s.type}</span>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.82rem' }}>
                    {s.type === 'http' ? s.url : `${s.command} ${(s.args || []).join(' ')}`}
                  </td>
                  <td>
                    <button className="btn-danger" onClick={() => handleDelete(s.name)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
