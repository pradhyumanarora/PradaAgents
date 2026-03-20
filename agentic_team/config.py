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
    model_name: str = "gpt-5.3-chat"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 16384
    # Azure OpenAI fields (set these to use Azure instead of OpenAI)
    azure_endpoint: Optional[str] = None
    azure_api_version: str = "2024-12-01-preview"

    @property
    def is_azure(self) -> bool:
        return bool(self.azure_endpoint)

    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Load configuration from environment variables."""
        return cls(
            model_name=os.getenv("OPENAI_MODEL", "gpt-5.3-chat"),
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MODEL_MAX_TOKENS", "16384")),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
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
