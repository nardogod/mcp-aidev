"""
Agent configuration management
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AgentConfig:
    """Configuration for the LangGraph Agent"""
    
    # LLM Provider
    llm_provider: str = None
    llm_model: str = None
    
    # API Keys
    groq_api_key: str = None
    anthropic_api_key: str = None
    
    # MCP Server
    mcp_server_url: str = None
    
    # Agent Settings
    max_phases: int = 10
    auto_continue: bool = False
    project_base_path: str = None  # Base path for project files
    
    def __post_init__(self):
        """Load from environment variables"""
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.mcp_server_url = os.getenv(
            "MCP_SERVER_URL", 
            "https://mcp-aidev.onrender.com"
        )
        self.project_base_path = os.getenv("PROJECT_BASE_PATH", None)
        
        # Set default model based on provider
        if self.llm_model is None:
            if self.llm_provider == "groq":
                self.llm_model = "llama-3.3-70b-versatile"
            elif self.llm_provider == "anthropic":
                self.llm_model = "claude-sonnet-4-20250514"
            elif self.llm_provider == "ollama":
                self.llm_model = "llama3.1"
    
    def validate(self) -> bool:
        """Validate configuration"""
        if self.llm_provider not in ["groq", "anthropic", "ollama"]:
            raise ValueError(f"Invalid LLM provider: {self.llm_provider}")
        
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for Groq provider")
        
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
        
        return True


# Global config instance
config = AgentConfig()

