# Agentic Development Team

A multi-agent AI team for software development using **AutoGen** framework with **MCP (Model Context Protocol)** integration. Agents collaborate through intelligent routing to design, implement, review, and secure your code.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SelectorGroupChat                             │
│                  (Intelligent Routing)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Architect   │  │  Developer   │  │   Code Reviewer      │   │
│  │    Agent     │  │    Agent     │  │      Agent           │   │
│  │              │  │              │  │                      │   │
│  │ • Design     │  │ • Implement  │  │ • Quality Review     │   │
│  │ • Patterns   │  │ • Write Code │  │ • Best Practices     │   │
│  │ • Specs      │  │ • Tests      │  │ • Suggestions        │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────────────────────────────────┐ │
│  │  Security    │  │         PR Review Agent                  │ │
│  │    Agent     │  │                                          │ │
│  │              │  │ • Fetch & Resolve PR Comments             │ │
│  │ • Vuln Scan  │  │ • Manage Approvals                       │ │
│  │ • Secrets    │  │ • Work Items                              │ │
│  │ • OWASP      │  │ • Code Review Coordination               │ │
│  └──────────────┘  └──────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
         ┌──────────────────┐  ┌────────────────┐
         │  MCP Servers     │  │  Your Custom   │
         │  (built-in)      │  │  MCP Servers   │
         │                  │  │                │
         │ • huggingface    │  │ • github       │
         │ • microsoft-docs │  │ • postgres     │
         │ • kustoMCP       │  │ • jira         │
         │ • adoMCP         │  │ • ...anything  │
         │ • DiscoveryMCP   │  │                │
         └──────────────────┘  └────────────────┘
                    ▲
         Configured via mcp_servers.yaml
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/pradhyumanarora/PradaAgents.git
cd PradaAgents
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."

# Linux / macOS
export OPENAI_API_KEY="sk-..."
```

### 3. (Optional) Configure MCP Servers

Edit `mcp_servers.yaml` to add, remove, or change MCP servers. See [Configuring MCP Servers](#-configuring-mcp-servers) below.

### 4. Run

```bash
python main.py
```

That's it. The agents will collaborate to complete the task defined in `main.py`.

---

## 📖 How to Build a Project with PradaAgents

### Step 1 — Write a Task

The agents are driven by a natural-language **task description**. Be specific about what you want each agent to do:

```python
import asyncio
from agentic_team.team import AgenticDevelopmentTeam

async def main():
    team = AgenticDevelopmentTeam(model_name="gpt-4o")

    task = """
    Build a REST API for a todo-list app.

    1. **ArchitectAgent**: Design the API — define endpoints, data model,
       and technology stack (FastAPI + SQLite).

    2. **DeveloperAgent**: Implement the endpoints:
       - POST /todos, GET /todos, PUT /todos/{id}, DELETE /todos/{id}
       - Include input validation and error handling.

    3. **SecurityAgent**: Review the implementation for vulnerabilities
       (injection, auth issues, data exposure).

    4. **CodeReviewerAgent**: Review code quality, suggest improvements.

    When all steps are complete, respond with TASK_COMPLETE.
    """

    try:
        result = await team.run(task)
        print(f"Messages exchanged: {len(result.messages)}")
    finally:
        await team.close()

asyncio.run(main())
```

### Step 2 — Understand Agent Routing

The team uses **SelectorGroupChat** — an LLM picks the best agent for each turn based on conversation context. You can influence routing by:

- **Mentioning agent names** in the task (e.g. "ArchitectAgent: design...")
- **Using keywords** that map to agents (e.g. "security" → SecurityAgent)
- **Ordering your instructions** — the first agent mentioned tends to go first

### Step 3 — Customize for Your Workflow

**Change the model:**
```python
team = AgenticDevelopmentTeam(model_name="gpt-4o-mini")
```

**Change max iterations:**
```python
team = AgenticDevelopmentTeam(model_name="gpt-4o", max_iterations=40)
```

**Use keyword-based routing** (deterministic instead of LLM-based):
```python
result = await team.run_with_custom_selector(task)
```

### Step 4 — Run & Iterate

```bash
python main.py
```

Watch the agents collaborate in your terminal. Each agent's output is labeled with its name. The conversation ends when an agent says `TASK_COMPLETE`, `TERMINATE`, or the max iteration limit is reached.

---

## 🔧 Configuring MCP Servers

MCP servers give agents access to external tools (Azure DevOps, GitHub, databases, docs, etc.). Configuration lives in **`mcp_servers.yaml`** at the project root.

### Default Servers (included)

| Server | Type | Purpose |
|--------|------|---------|
| `huggingface` | HTTP | ML model & dataset search |
| `microsoft-docs` | HTTP | Microsoft documentation |
| `kustoMCP` | stdio | Kusto database queries |
| `adoMCP` | stdio | Azure DevOps (PRs, work items, repos) |
| `DiscoveryMCP` | HTTP | Custom discovery service |

### Adding Your Own

Edit `mcp_servers.yaml` and add entries:

```yaml
# HTTP server — just needs a URL
github:
  type: "http"
  url: "https://api.github.com/mcp"

# stdio server — runs a local process
postgres:
  type: "stdio"
  command: "npx"
  args: ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"]

# With environment variables (use ${VAR} syntax)
gitlab:
  type: "stdio"
  command: "npx"
  args: ["-y", "@modelcontextprotocol/server-gitlab"]
  env:
    GITLAB_TOKEN: "${GITLAB_TOKEN}"
```

### Removing Servers You Don't Need

Just delete or comment out the entry in `mcp_servers.yaml`:

```yaml
# Don't use Kusto? Comment it out:
# kustoMCP:
#   type: "stdio"
#   command: "npx"
#   args: ["-y", "@mcp-apps/kusto-mcp-server"]
```

### Using a Custom Config Path

```bash
# Point to a different config file
$env:MCP_SERVERS_CONFIG = "C:\path\to\my_servers.yaml"
python main.py
```

If `mcp_servers.yaml` doesn't exist and no env var is set, the built-in defaults are used automatically.

### Agent → Server Mapping

Which agents can use which MCP servers is defined in `agentic_team/mcp_integration.py` via `AGENT_MCP_MAPPING`:

| Agent | MCP Servers |
|-------|-------------|
| ArchitectAgent | microsoft-docs, huggingface |
| DeveloperAgent | microsoft-docs, kustoMCP |
| CodeReviewerAgent | microsoft-docs |
| SecurityAgent | microsoft-docs |
| PRReviewAgent | adoMCP |

To change this, edit the `AGENT_MCP_MAPPING` dict in `mcp_integration.py`.

---

## 🎯 Example Projects

### Build a Feature (End-to-End)

```python
task = """
Design and implement a user authentication system with JWT tokens.

1. ArchitectAgent: Design auth architecture (login, signup, token refresh)
2. DeveloperAgent: Implement with FastAPI + python-jose + passlib
3. SecurityAgent: Audit for OWASP Top 10 vulnerabilities
4. CodeReviewerAgent: Final code quality review

When complete, respond with TASK_COMPLETE.
"""
```

### PR Review Workflow

```python
task = """
Review pull request #42 in our Azure DevOps project.

1. PRReviewAgent: Fetch PR details and list all comments
2. CodeReviewerAgent: Analyze the feedback and prioritize issues
3. SecurityAgent: Check for security-related concerns
4. DeveloperAgent: Implement fixes for the review comments
5. PRReviewAgent: Resolve comments and prepare for approval

When complete, respond with TASK_COMPLETE.
"""
```

### Security Audit

```python
task = """
Perform a full security audit of the authentication module:
1. Scan for hardcoded secrets and credentials
2. Check for SQL injection and XSS vulnerabilities
3. Review password hashing and session management
4. Verify OWASP Top 10 compliance
Provide a detailed security report with risk levels.

When complete, respond with TASK_COMPLETE.
"""
```

### Architecture Review

```python
task = """
Review the current microservices architecture:
1. ArchitectAgent: Analyze the component design and identify issues
2. SecurityAgent: Check for insecure communication patterns
3. CodeReviewerAgent: Review for maintainability and coupling

When complete, respond with TASK_COMPLETE.
"""
```

---

## 📦 Project Structure

```
PradaAgents/
├── main.py                    # CLI entry point — edit your task here
├── mcp_servers.yaml           # MCP server configuration (customizable)
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── docker-compose.yml         # Docker Compose — run everything
├── Dockerfile.backend         # Backend container (FastAPI + agents)
├── Dockerfile.frontend        # Frontend container (React + Nginx)
├── .dockerignore
├── .gitignore
├── README.md
│
├── agentic_team/              # Core agent framework
│   ├── __init__.py
│   ├── config.py              # Model & team configuration
│   ├── team.py                # Team orchestration (SelectorGroupChat)
│   ├── mcp_integration.py     # MCP server loading & agent mapping
│   └── agents/
│       ├── __init__.py
│       ├── architect_agent.py
│       ├── developer_agent.py
│       ├── code_reviewer_agent.py
│       ├── security_agent.py
│       └── pr_review_agent.py
│
├── backend/                   # FastAPI backend (REST + SSE)
│   ├── __init__.py
│   ├── app.py                 # API endpoints
│   └── requirements.txt
│
└── frontend/                  # React UI (Vite + Nginx)
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── nginx.conf             # Nginx reverse-proxy config
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css
        ├── api.js             # API client
        └── components/
            ├── TaskPanel.jsx
            ├── McpServersPanel.jsx
            └── AgentsPanel.jsx
```

---

## 🐳 Docker — Run the Full Stack

### Prerequisites

- Docker & Docker Compose installed
- An OpenAI API key

### Quick Start

```bash
# 1. Set your API key (or create a .env file)
echo "OPENAI_API_KEY=sk-..." > .env

# 2. Build and run both containers
docker-compose up --build

# 3. Open the UI
#    http://localhost:3000
```

| Service  | Container               | Port | Description |
|----------|-------------------------|------|-------------|
| Backend  | `pradaagent-backend`    | 8080 | FastAPI API (agents + MCP CRUD) |
| Frontend | `pradaagent-frontend`   | 3000 | React UI served by Nginx |

### What the UI Exposes

| Page | Feature |
|------|---------|
| **Run Task** | Write a task, pick a model, set max iterations, and stream real-time agent messages |
| **MCP Servers** | Add / delete MCP server configurations (`mcp_servers.yaml` is updated live) |
| **Agents** | View the five agents and their mapped MCP servers |

### Backend API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/health` | Health check |
| `GET`  | `/api/agents` | List agents & their MCP mappings |
| `GET`  | `/api/mcp-servers` | List configured MCP servers |
| `POST` | `/api/mcp-servers` | Add a new MCP server |
| `PUT`  | `/api/mcp-servers/{name}` | Update an MCP server |
| `DELETE` | `/api/mcp-servers/{name}` | Remove an MCP server |
| `POST` | `/api/tasks` | Start a new task (returns session_id) |
| `GET`  | `/api/tasks/{id}/stream` | SSE stream of agent messages |
| `GET`  | `/api/tasks/{id}` | Get task status & messages |

### Stopping

```bash
docker-compose down
```

---

## 🤖 Agent Reference

| Agent | Role | Triggered By |
|-------|------|-------------|
| **ArchitectAgent** | System design, patterns, specs, interfaces | "design", "architect", "structure", "component" |
| **DeveloperAgent** | Code implementation, tests, documentation | "implement", "write code", "create file", "fix bug" |
| **CodeReviewerAgent** | Code review, quality checks, best practices | "review", "check", "analyze code", "code quality" |
| **SecurityAgent** | Vulnerability scanning, secrets detection, OWASP | "security", "vulnerability", "secret", "credential" |
| **PRReviewAgent** | PR comments, approvals, Azure DevOps workflow | "pr", "pull request", "comment", "resolve" |

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | **Required.** Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | Model to use |
| `MODEL_TEMPERATURE` | `0.7` | Response creativity (0.0–1.0) |
| `MODEL_MAX_TOKENS` | `4096` | Max tokens per response |
| `TEAM_MAX_ITERATIONS` | `25` | Max messages before stopping |
| `MCP_SERVERS_CONFIG` | `mcp_servers.yaml` | Path to custom MCP config |

### Programmatic Configuration

```python
from agentic_team.team import AgenticDevelopmentTeam

team = AgenticDevelopmentTeam(
    model_name="gpt-4o",       # or "gpt-4o-mini" for lower cost
    api_key="sk-...",          # or use OPENAI_API_KEY env var
    max_iterations=30,
)
```

---

## 📚 Resources

- [AutoGen Documentation](https://microsoft.github.io/autogen/stable/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [Azure DevOps REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test by running the team with a sample task
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.
