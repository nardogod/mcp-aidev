"""
LLM Provider Abstraction - Easy switching between Groq, Claude, Ollama
"""
import os
from enum import Enum
from typing import Union

from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GROQ = "groq"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


def get_llm(
    provider: Union[str, LLMProvider] = "groq",
    model: str = None,
    temperature: float = 0.7
):
    """
    Get LLM instance based on provider.
    
    Easy to switch providers - just change the provider parameter!
    
    Args:
        provider: LLM provider (groq, anthropic, ollama)
        model: Model name (optional, uses defaults)
        temperature: Sampling temperature
        
    Returns:
        LangChain chat model instance
        
    Example:
        # Use Groq (free!)
        llm = get_llm("groq")
        
        # Switch to Claude (paid but better)
        llm = get_llm("anthropic")
        
        # Use local Ollama (free, offline)
        llm = get_llm("ollama")
    """
    if isinstance(provider, str):
        provider = provider.lower()
    
    if provider == LLMProvider.GROQ or provider == "groq":
        return ChatGroq(
            model=model or os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=temperature
        )
    
    elif provider == LLMProvider.ANTHROPIC or provider == "anthropic":
        return ChatAnthropic(
            model=model or "claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=temperature
        )
    
    elif provider == LLMProvider.OLLAMA or provider == "ollama":
        return ChatOllama(
            model=model or "llama3.1",
            temperature=temperature
        )
    
    else:
        raise ValueError(
            f"Invalid provider: {provider}. "
            f"Supported: {[p.value for p in LLMProvider]}"
        )

