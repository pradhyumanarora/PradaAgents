"""
MCP Integration for the Agentic Team.

This module provides utilities for integrating MCP (Model Context Protocol)
servers with the AutoGen agents.

MCP servers are loaded from ``mcp_servers.yaml`` in the project root.
If the file is missing, the built-in defaults are used.
Users can add / remove / modify servers by editing that YAML file.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

import yaml


_ENV_VAR_PATTERN = re.compile(r"\$\{(\w+)\}")


def _expand_env_vars(value: str) -> str:
    """Replace ${VAR} placeholders with environment variable values."""
    def _replacer(match):
        return os.environ.get(match.group(1), match.group(0))
    return _ENV_VAR_PATTERN.sub(_replacer, value)


class MCPServerType(Enum):
    """Types of MCP servers available."""
    HUGGINGFACE = "huggingface"
    MICROSOFT_DOCS = "microsoft-docs"
    KUSTO = "kustoMCP"
    AZURE_DEVOPS = "adoMCP"
    DISCOVERY = "DiscoveryMCP"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    server_type: str  # "http" or "stdio"
    url: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None


# --- Built-in defaults (used when mcp_servers.yaml is absent) --------------

_DEFAULT_MCP_SERVERS: Dict[str, MCPServerConfig] = {
    "huggingface": MCPServerConfig(
        name="huggingface",
        server_type="http",
        url="https://hf.co/mcp"
    ),
    "microsoft-docs": MCPServerConfig(
        name="microsoft-docs",
        server_type="http",
        url="https://learn.microsoft.com/api/mcp"
    ),
    "kustoMCP": MCPServerConfig(
        name="kustoMCP",
        server_type="stdio",
        command="npx",
        args=["-y", "@mcp-apps/kusto-mcp-server"]
    ),
    "adoMCP": MCPServerConfig(
        name="adoMCP",
        server_type="stdio",
        command="npx",
        args=["@mcp-apps/azure-devops-mcp-server"]
    ),
    "DiscoveryMCP": MCPServerConfig(
        name="DiscoveryMCP",
        server_type="http",
        url="http://localhost:8000/mcp"
    ),
}


def _load_servers_from_yaml(yaml_path: str) -> Dict[str, MCPServerConfig]:
    """Parse mcp_servers.yaml into a dict of MCPServerConfig."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    servers: Dict[str, MCPServerConfig] = {}
    for name, cfg in raw.items():
        env_map = None
        if cfg.get("env"):
            env_map = {k: _expand_env_vars(str(v)) for k, v in cfg["env"].items()}
        args = cfg.get("args")
        if args:
            args = [_expand_env_vars(str(a)) for a in args]
        servers[name] = MCPServerConfig(
            name=name,
            server_type=cfg.get("type", "http"),
            url=cfg.get("url"),
            command=cfg.get("command"),
            args=args,
            env=env_map,
        )
    return servers


def _resolve_mcp_servers() -> Dict[str, MCPServerConfig]:
    """
    Load MCP servers.  Resolution order:
      1. Path in MCP_SERVERS_CONFIG env var
      2. mcp_servers.yaml in the project root
      3. Built-in defaults
    """
    yaml_path = os.getenv("MCP_SERVERS_CONFIG")
    if yaml_path is None:
        candidate = Path(__file__).resolve().parent.parent / "mcp_servers.yaml"
        if candidate.exists():
            yaml_path = str(candidate)

    if yaml_path and Path(yaml_path).exists():
        return _load_servers_from_yaml(yaml_path)

    return dict(_DEFAULT_MCP_SERVERS)


# Module-level dict that the rest of the codebase uses
MCP_SERVERS: Dict[str, MCPServerConfig] = _resolve_mcp_servers()


def get_mcp_server_params(server_name: str):
    """
    Get the MCP server parameters for use with McpWorkbench.
    
    Args:
        server_name: The name of the MCP server
        
    Returns:
        Appropriate server params for McpWorkbench
    """
    from autogen_ext.tools.mcp import StdioServerParams, SseServerParams
    
    config = MCP_SERVERS.get(server_name)
    if not config:
        raise ValueError(f"Unknown MCP server: {server_name}")
    
    if config.server_type == "stdio":
        kwargs = {"command": config.command, "args": config.args or []}
        if config.env:
            kwargs["env"] = config.env
        return StdioServerParams(**kwargs)
    elif config.server_type == "http":
        return SseServerParams(url=config.url)
    else:
        raise ValueError(f"Unsupported server type: {config.server_type}")


# Tool mappings - which tools each agent should use
AGENT_MCP_MAPPING = {
    "ArchitectAgent": [
        # Architect can use docs for research
        "microsoft-docs",
        "huggingface",  # For ML architecture decisions
    ],
    "DeveloperAgent": [
        # Developer uses docs and can query data
        "microsoft-docs",
        "kustoMCP",
    ],
    "CodeReviewerAgent": [
        # Reviewer uses docs for best practices
        "microsoft-docs",
    ],
    "SecurityAgent": [
        # Security agent uses docs for security guidelines
        "microsoft-docs",
    ],
    "PRReviewAgent": [
        # PR Review agent heavily uses Azure DevOps
        "adoMCP",
    ],
}


def get_agent_mcp_servers(agent_name: str) -> List[str]:
    """
    Get the list of MCP servers an agent should have access to.
    
    Args:
        agent_name: The name of the agent
        
    Returns:
        List of MCP server names
    """
    return AGENT_MCP_MAPPING.get(agent_name, [])


# Usage instructions for MCP tools in VS Code Agent Mode
MCP_USAGE_GUIDE = """
# Using MCP Tools with the Agentic Team

When running in VS Code with GitHub Copilot Agent mode, the MCP tools are
automatically available. Here's how each agent can use them:

## PRReviewAgent - Azure DevOps MCP (adoMCP)
The PR Review Agent has access to these ADO MCP tools:
- `mcp_adomcp_list-build-runs`: List recent build runs
- `mcp_adomcp_list-release-runs`: List recent release runs
- `mcp_adomcp_update-work-item`: Update work items
- `mcp_adomcp_create-test-case`: Create test cases
- `mcp_adomcp_get-test-case-details`: Get test case details
- `mcp_adomcp_git-commit-changes`: Commit changes
- `activate_pull_request_analysis_tools`: Analyze PRs
- `activate_git_repository_management_tools`: Manage repos

## All Agents - Microsoft Docs MCP
- `mcp_microsoft-doc_microsoft_docs_search`: Search MS documentation
- `mcp_microsoft-doc_microsoft_docs_fetch`: Fetch full doc pages

## Developer/Architect - HuggingFace MCP
- `mcp_huggingface_model_search`: Search for ML models
- `mcp_huggingface_dataset_search`: Search for datasets
- `mcp_huggingface_hf_doc_search`: Search HF documentation

## Developer - Kusto MCP
- `mcp_kustomcp_execute_query`: Run Kusto queries
- `mcp_kustomcp_list_tables`: List database tables
- `mcp_kustomcp_get_table_schema`: Get table schema

To use these tools, simply describe what you need and the appropriate
MCP tool will be invoked automatically through VS Code's agent mode.
"""
