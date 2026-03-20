"""
Configuration settings for the Agentic Team.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AzureDevOpsConfig:
    """Azure DevOps configuration for PR Review Agent."""
    organization_url: str
    project_name: str
    repository_name: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "AzureDevOpsConfig":
        """Load configuration from environment variables."""
        return cls(
            organization_url=os.getenv("ADO_ORGANIZATION_URL", "https://dev.azure.com/your-org"),
            project_name=os.getenv("ADO_PROJECT_NAME", "your-project"),
            repository_name=os.getenv("ADO_REPOSITORY_NAME"),
        )


@dataclass
class ModelConfig:
    """Model configuration for agents."""
    model_name: str = "gpt-4o"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    
    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Load configuration from environment variables."""
        return cls(
            model_name=os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MODEL_MAX_TOKENS", "4096")),
        )


@dataclass
class TeamConfig:
    """Overall team configuration."""
    model_config: ModelConfig
    ado_config: AzureDevOpsConfig
    max_iterations: int = 25
    allow_repeated_speaker: bool = True
    
    @classmethod
    def from_env(cls) -> "TeamConfig":
        """Load all configuration from environment variables."""
        return cls(
            model_config=ModelConfig.from_env(),
            ado_config=AzureDevOpsConfig.from_env(),
            max_iterations=int(os.getenv("TEAM_MAX_ITERATIONS", "25")),
            allow_repeated_speaker=os.getenv("ALLOW_REPEATED_SPEAKER", "true").lower() == "true",
        )
