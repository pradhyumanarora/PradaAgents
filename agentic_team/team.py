"""
Agentic Development Team - Main team orchestration using AutoGen SelectorGroupChat.

This module creates and manages a team of specialized agents for the software
development lifecycle:
- Architect Agent: Designs system architecture
- Developer Agent: Implements code
- Code Reviewer Agent: Reviews code quality
- Security Agent: Ensures security best practices
- PR Review Agent: Manages Azure DevOps PR workflow

The team uses MCP tools available in VS Code for enhanced capabilities.
"""

import asyncio
from typing import Optional, Sequence

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .agents import (
    create_architect_agent,
    create_developer_agent,
    create_code_reviewer_agent,
    create_security_agent,
    create_pr_review_agent,
)
from .config import TeamConfig


# Selector prompt for intelligent agent routing
SELECTOR_PROMPT = """You are coordinating a software development team. Select the most appropriate agent for the next step.

{roles}

Current conversation context:
{history}

## Agent Selection Guidelines:

1. **ArchitectAgent** - Select when:
   - Starting a new feature or system design
   - Discussing architecture, components, or interfaces
   - Need to define technical specifications
   - Design decisions are required

2. **DeveloperAgent** - Select when:
   - Architecture is defined and code needs to be written
   - Implementing features or fixing bugs
   - Writing tests
   - Code modifications are requested

3. **CodeReviewerAgent** - Select when:
   - Code has been written and needs review
   - Quality assessment is needed
   - Looking for bugs or improvements
   - Verifying code standards

4. **SecurityAgent** - Select when:
   - Security analysis is needed
   - Checking for vulnerabilities
   - Reviewing authentication/authorization
   - Secrets or sensitive data handling

5. **PRReviewAgent** - Select when:
   - Managing pull request workflow
   - Addressing PR comments
   - Coordinating final approval
   - Azure DevOps operations are needed

Read the conversation and select the single most appropriate agent from {participants}.
Only return the agent name.
"""


def create_selector_function():
    """
    Create a custom selector function for specialized agent routing.
    
    Returns:
        A selector function that routes to appropriate agents based on context
    """
    def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
        if not messages:
            return "ArchitectAgent"  # Start with architect for new tasks
        
        last_message = messages[-1]
        last_content = last_message.content if hasattr(last_message, 'content') else ""
        
        if isinstance(last_content, str):
            content_lower = last_content.lower()
            
            # Route based on keywords in the last message
            if any(word in content_lower for word in ['pr', 'pull request', 'comment', 'resolve', 'ado', 'azure devops']):
                return "PRReviewAgent"
            
            if any(word in content_lower for word in ['security', 'vulnerability', 'secret', 'credential', 'attack']):
                return "SecurityAgent"
            
            if any(word in content_lower for word in ['review', 'check', 'analyze code', 'code quality']):
                return "CodeReviewerAgent"
            
            if any(word in content_lower for word in ['implement', 'write code', 'create file', 'fix bug']):
                return "DeveloperAgent"
            
            if any(word in content_lower for word in ['design', 'architect', 'structure', 'component']):
                return "ArchitectAgent"
        
        # Let the model decide if no clear routing
        return None
    
    return selector_func


class AgenticDevelopmentTeam:
    """
    A coordinated team of AI agents for software development.
    
    This team uses AutoGen's SelectorGroupChat to intelligently route tasks
    to specialized agents based on the development workflow.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        max_iterations: int = 25,
    ):
        """
        Initialize the Agentic Development Team.
        
        Args:
            model_name: The OpenAI model to use
            api_key: Optional API key (uses OPENAI_API_KEY env var if not provided)
            max_iterations: Maximum number of message iterations
        """
        # Create model client
        client_kwargs = {"model": model_name}
        if api_key:
            client_kwargs["api_key"] = api_key
        
        self.model_client = OpenAIChatCompletionClient(**client_kwargs)
        self.max_iterations = max_iterations
        
        # Create agents
        self.architect_agent = create_architect_agent(self.model_client)
        self.developer_agent = create_developer_agent(self.model_client)
        self.code_reviewer_agent = create_code_reviewer_agent(self.model_client)
        self.security_agent = create_security_agent(self.model_client)
        self.pr_review_agent = create_pr_review_agent(self.model_client)
        
        # Create termination conditions
        self.termination = (
            TextMentionTermination("TASK_COMPLETE") |
            TextMentionTermination("TERMINATE") |
            MaxMessageTermination(max_messages=max_iterations)
        )
        
        # Create the team
        self.team = SelectorGroupChat(
            participants=[
                self.architect_agent,
                self.developer_agent,
                self.code_reviewer_agent,
                self.security_agent,
                self.pr_review_agent,
            ],
            model_client=self.model_client,
            termination_condition=self.termination,
            selector_prompt=SELECTOR_PROMPT,
            allow_repeated_speaker=True,
        )
    
    async def run(self, task: str):
        """
        Run the team on a given task.
        
        Args:
            task: The task description to work on
            
        Returns:
            TaskResult with the conversation history
        """
        return await Console(self.team.run_stream(task=task))
    
    async def run_with_custom_selector(self, task: str):
        """
        Run the team with a custom selector function for more controlled routing.
        
        Args:
            task: The task description to work on
            
        Returns:
            TaskResult with the conversation history
        """
        # Create team with custom selector
        team_with_selector = SelectorGroupChat(
            participants=[
                self.architect_agent,
                self.developer_agent,
                self.code_reviewer_agent,
                self.security_agent,
                self.pr_review_agent,
            ],
            model_client=self.model_client,
            termination_condition=self.termination,
            selector_prompt=SELECTOR_PROMPT,
            selector_func=create_selector_function(),
            allow_repeated_speaker=True,
        )
        
        return await Console(team_with_selector.run_stream(task=task))
    
    async def reset(self):
        """Reset the team state for a new task."""
        await self.team.reset()
    
    async def close(self):
        """Clean up resources."""
        await self.model_client.close()


async def create_team_with_mcp_workbench():
    """
    Create a team that uses MCP Workbench for enhanced tool access.
    
    This function demonstrates how to integrate MCP tools with the agents.
    The MCP servers are accessed via VS Code's MCP configuration.
    
    Note: MCP tools are available through VS Code's agent mode.
    When running in VS Code with MCP servers configured, agents can
    access these tools through the McpWorkbench.
    
    Available MCP servers in your config:
    - huggingface: HuggingFace model/dataset search
    - microsoft-docs: Microsoft documentation search
    - kustoMCP: Kusto database queries
    - adoMCP: Azure DevOps operations (PRs, work items, repos)
    - DiscoveryMCP: Custom discovery service
    """
    from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
    
    # Example: Create ADO MCP workbench for PR Review Agent
    ado_mcp_server = StdioServerParams(
        command="npx",
        args=["@mcp-apps/azure-devops-mcp-server"]
    )
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    
    # Create PR Review Agent with MCP Workbench
    async with McpWorkbench(ado_mcp_server) as workbench:
        pr_agent_with_mcp = AssistantAgent(
            name="PRReviewAgent",
            description="PR Review Agent with Azure DevOps MCP tools",
            model_client=model_client,
            workbench=workbench,
            system_message="""You are a PR Review Agent with access to Azure DevOps MCP tools.
            Use the available tools to:
            - List and get PR details
            - Read PR comments
            - Analyze code changes
            - Manage work items
            - Resolve PR comments
            """,
            reflect_on_tool_use=True,
        )
        
        # Run a task with the MCP-enabled agent
        result = await pr_agent_with_mcp.run(
            task="List the recent pull requests and their status"
        )
        
        return result


# Main entry point for running the team
async def main():
    """Main entry point for running the Agentic Development Team."""
    print("=" * 60)
    print("Agentic Development Team - AutoGen Framework")
    print("=" * 60)
    print()
    print("Available Agents:")
    print("  1. ArchitectAgent - System design and architecture")
    print("  2. DeveloperAgent - Code implementation")
    print("  3. CodeReviewerAgent - Code quality review")
    print("  4. SecurityAgent - Security analysis")
    print("  5. PRReviewAgent - Azure DevOps PR management")
    print()
    print("MCP Tools Available:")
    print("  - Azure DevOps (adoMCP): PR management, work items")
    print("  - Microsoft Docs: Documentation search")
    print("  - HuggingFace: Model/dataset search")
    print("  - Kusto: Database queries")
    print()
    
    # Create and run the team
    team = AgenticDevelopmentTeam(model_name="gpt-4o")
    
    try:
        # Example task - you can modify this
        task = """
        I need help reviewing and resolving comments on a pull request.
        
        Please:
        1. First, understand what changes are in the PR
        2. Review the code for quality and security issues
        3. Address any reviewer comments
        4. Ensure the code is ready for merge
        
        Use the Azure DevOps MCP tools to interact with the PR.
        
        When all tasks are complete, respond with TASK_COMPLETE.
        """
        
        result = await team.run(task)
        print("\n" + "=" * 60)
        print("Task Completed!")
        print("=" * 60)
        
    finally:
        await team.close()


if __name__ == "__main__":
    asyncio.run(main())
