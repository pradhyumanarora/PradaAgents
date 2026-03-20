# Agentic Development Team

A multi-agent AI team for software development using **AutoGen** framework with **MCP (Model Context Protocol)** integration.

## 🏗️ Architecture

The team consists of 5 specialized agents that work together:

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
│  │              │  │ • Azure DevOps MCP Integration           │ │
│  │ • Vuln Scan  │  │ • Fetch & Resolve PR Comments            │ │
│  │ • Secrets    │  │ • Manage Approvals                       │ │
│  │ • OWASP      │  │ • Work Items                             │ │
│  └──────────────┘  └──────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │        MCP Servers            │
              ├───────────────────────────────┤
              │ • adoMCP (Azure DevOps)       │
              │ • microsoft-docs              │
              │ • huggingface                 │
              │ • kustoMCP                    │
              │ • DiscoveryMCP                │
              └───────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key"

# Or copy and edit .env.example
cp .env.example .env
```

### 3. Run the Team

```bash
python main.py
```

## 📦 Project Structure

```
PradaAgent/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── README.md                 # This file
│
└── agentic_team/
    ├── __init__.py
    ├── config.py             # Configuration classes
    ├── team.py               # Main team orchestration
    ├── mcp_integration.py    # MCP server utilities
    │
    ├── agents/
    │   ├── __init__.py
    │   ├── architect_agent.py
    │   ├── developer_agent.py
    │   ├── code_reviewer_agent.py
    │   ├── security_agent.py
    │   └── pr_review_agent.py
    │
    └── tools/                # (Optional custom tools)
        ├── __init__.py
        ├── code_tools.py
        ├── security_tools.py
        └── ado_tools.py
```

## 🔧 MCP Integration

The agents leverage MCP servers configured in VS Code:

| Server | Purpose | Used By |
|--------|---------|---------|
| `adoMCP` | Azure DevOps operations | PRReviewAgent |
| `microsoft-docs` | Documentation search | All Agents |
| `huggingface` | ML model/dataset search | Architect, Developer |
| `kustoMCP` | Database queries | Developer |
| `DiscoveryMCP` | Custom discovery | All Agents |

### Available ADO MCP Tools

The PR Review Agent can use these Azure DevOps tools:

- `mcp_adomcp_list-build-runs` - List build runs
- `mcp_adomcp_list-release-runs` - List releases  
- `mcp_adomcp_update-work-item` - Update work items
- `mcp_adomcp_git-commit-changes` - Commit changes
- `activate_pull_request_analysis_tools` - Analyze PRs
- `activate_git_repository_management_tools` - Repo management

## 🎯 Usage Examples

### Example 1: Full Development Workflow

```python
import asyncio
from agentic_team.team import AgenticDevelopmentTeam

async def main():
    team = AgenticDevelopmentTeam(model_name="gpt-4o")
    
    task = """
    Design and implement a REST API endpoint for user registration.
    Include input validation, password hashing, and proper error handling.
    Review for security vulnerabilities before completion.
    """
    
    await team.run(task)
    await team.close()

asyncio.run(main())
```

### Example 2: PR Review Workflow

```python
task = """
Use Azure DevOps MCP to:
1. Get details of PR #123 in project 'MyProject'
2. List all active comments
3. Analyze the code changes for issues
4. Suggest resolutions for reviewer feedback
5. Mark comments as resolved when addressed
"""
```

### Example 3: Security Audit

```python
task = """
Perform a security audit of the authentication module:
1. Scan for hardcoded secrets
2. Check for SQL injection vulnerabilities
3. Review password handling
4. Verify session management
Provide a detailed security report.
"""
```

## 🤖 Agent Descriptions

### ArchitectAgent
- Designs system architecture and components
- Recommends design patterns (SOLID, DDD, etc.)
- Creates technical specifications
- Defines interfaces and data models

### DeveloperAgent  
- Implements features based on specs
- Writes clean, testable code
- Creates unit and integration tests
- Follows coding standards

### CodeReviewerAgent
- Performs thorough code reviews
- Identifies bugs and code smells
- Suggests improvements
- Verifies coding standards

### SecurityAgent
- Scans for vulnerabilities (OWASP Top 10)
- Detects exposed secrets
- Reviews authentication/authorization
- Provides security recommendations

### PRReviewAgent
- Manages Azure DevOps pull requests
- Fetches and categorizes PR comments
- Coordinates issue resolution
- Handles PR approval workflow

## ⚙️ Configuration

Edit `agentic_team/config.py` or use environment variables:

```python
# In code
team = AgenticDevelopmentTeam(
    model_name="gpt-4o",
    max_iterations=25,
)
```

```bash
# Environment variables
OPENAI_MODEL=gpt-4o
TEAM_MAX_ITERATIONS=25
ADO_ORGANIZATION_URL=https://dev.azure.com/myorg
ADO_PROJECT_NAME=MyProject
```

## 📚 Documentation

- [AutoGen Documentation](https://microsoft.github.io/autogen/stable/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Azure DevOps REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the team to test
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.
