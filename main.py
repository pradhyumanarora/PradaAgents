"""
Main entry point for the Agentic Development Team.

This script demonstrates how to run the team of specialized agents
for software development tasks.
"""

import asyncio
import os
from agentic_team.team import AgenticDevelopmentTeam


async def run_development_task():
    """Run a sample development task with the agentic team."""
    
    print("=" * 70)
    print("  AGENTIC DEVELOPMENT TEAM")
    print("  Powered by AutoGen + MCP Tools")
    print("=" * 70)
    print()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set in environment")
        print("   Set it with: $env:OPENAI_API_KEY = 'your-key'")
        print()
    
    # Create the team
    team = AgenticDevelopmentTeam(
        model_name="gpt-4o",
        max_iterations=30
    )
    
    print("📋 Team Members:")
    print("   • ArchitectAgent - Designs system architecture")
    print("   • DeveloperAgent - Writes and implements code")
    print("   • CodeReviewerAgent - Reviews code quality")
    print("   • SecurityAgent - Ensures security best practices")
    print("   • PRReviewAgent - Manages Azure DevOps PRs")
    print()
    
    print("🔧 Available MCP Tools:")
    print("   • Azure DevOps (adoMCP) - PR management, work items, repos")
    print("   • Microsoft Docs - Documentation search and fetch")
    print("   • HuggingFace - Model and dataset discovery")
    print("   • Kusto - Database queries")
    print()
    
    # Example task - modify as needed
    task = """
    We need to implement a new user authentication feature. Please:
    
    1. **Architect**: Design the authentication system architecture
       - Define components for login, token management, and session handling
       - Recommend appropriate security patterns
    
    2. **Developer**: Implement the basic authentication module
       - Create the core authentication classes
       - Include proper error handling
    
    3. **Security Agent**: Review the design and implementation for security
       - Check for common vulnerabilities
       - Ensure secure credential handling
    
    4. **Code Reviewer**: Review the code quality
       - Check for best practices
       - Suggest improvements
    
    When all steps are complete, respond with TASK_COMPLETE.
    """
    
    print("📝 Task:")
    print("-" * 50)
    print(task)
    print("-" * 50)
    print()
    
    try:
        print("🚀 Starting team execution...")
        print()
        
        result = await team.run(task)
        
        print()
        print("=" * 70)
        print("✅ Task Execution Complete!")
        print("=" * 70)
        
        if result:
            print(f"\nMessages exchanged: {len(result.messages)}")
            print(f"Stop reason: {result.stop_reason}")
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        raise
    
    finally:
        await team.close()
        print("\n🔒 Team resources cleaned up.")


async def run_pr_review_task():
    """Run a PR review task specifically using Azure DevOps MCP."""
    
    print("=" * 70)
    print("  PR REVIEW WORKFLOW")
    print("  Using Azure DevOps MCP")
    print("=" * 70)
    print()
    
    team = AgenticDevelopmentTeam(
        model_name="gpt-4o",
        max_iterations=25
    )
    
    # PR Review specific task
    task = """
    I need to review and resolve comments on a Pull Request in Azure DevOps.
    
    Please use the Azure DevOps MCP tools to:
    
    1. **PRReviewAgent**: Get the PR details and list all comments
       - Use ADO MCP to fetch PR information
       - Categorize comments by severity
    
    2. **CodeReviewerAgent**: Analyze the feedback
       - Understand what changes are requested
       - Prioritize the issues
    
    3. **SecurityAgent**: Check if there are any security-related comments
       - Address security concerns
       - Verify fixes don't introduce vulnerabilities
    
    4. **DeveloperAgent**: Implement fixes for the comments
       - Address code review feedback
       - Make necessary changes
    
    5. **PRReviewAgent**: Resolve the comments
       - Mark addressed comments as resolved
       - Prepare PR for final approval
    
    Note: You'll need to provide the PR ID and Azure DevOps organization details.
    
    When complete, respond with TASK_COMPLETE.
    """
    
    print("📝 Task: PR Review Workflow")
    print("-" * 50)
    
    try:
        result = await team.run(task)
        print("\n✅ PR Review Complete!")
        
    finally:
        await team.close()


if __name__ == "__main__":
    # Run the development task
    asyncio.run(run_development_task())
    
    # Alternatively, run the PR review task:
    # asyncio.run(run_pr_review_task())
