"""
LLM provider initialization and configuration.
Supports GitHub Models, OpenAI, Azure OpenAI, and Groq.
"""

import os
from typing import Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, AzureChatOpenAI

# Load environment variables
load_dotenv()

# Optional Groq support
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# =========================================================
# CORE LLM FACTORY
# =========================================================

def get_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    provider: Optional[str] = None,
):
    """
    Initialize and return an LLM instance.

    Supported providers:
    - github  (FREE tier, recommended)
    - openai
    - azure
    - groq
    """

    provider = (provider or os.getenv("MODEL_PROVIDER", "github")).lower()
    model_name = model_name or os.getenv("MODEL_NAME", "gpt-4o-mini")

    # =====================================================
    # GITHUB MODELS (FREE – RECOMMENDED)
    # =====================================================
    if provider == "github":
        api_key = os.getenv("GITHUB_TOKEN")
        if not api_key:
            raise ValueError(
                "GITHUB_TOKEN not found. "
                "Create one at https://github.com/settings/tokens "
                "with `models:read` permission."
            )

        return ChatOpenAI(
            model=model_name,  # MUST be full name: openai/gpt-4o-mini
            api_key=api_key,
            base_url="https://models.inference.ai.azure.com",
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # =====================================================
    # OPENAI
    # =====================================================
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        # Fix model name - remove 'openai/' prefix if present (used by GitHub Models)
        if model_name.startswith("openai/"):
            model_name = model_name.replace("openai/", "")
        
        # Default to gpt-4o-mini if not specified
        if not model_name or model_name == "openai/gpt-4o-mini":
            model_name = "gpt-4o-mini"

        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # =====================================================
    # AZURE OPENAI
    # =====================================================
    if provider == "azure":
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", model_name)

        if not api_key or not endpoint:
            raise ValueError(
                "Azure OpenAI requires AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT"
            )

        # Reasoning models (o1/o3/gpt-5) do NOT support temperature
        is_reasoning_model = any(x in deployment.lower() for x in ["o1", "o3", "gpt-5"])

        if is_reasoning_model:
            return AzureChatOpenAI(
                azure_deployment=deployment,
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version=api_version,
            )

        return AzureChatOpenAI(
            azure_deployment=deployment,
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # =====================================================
    # GROQ (FREE & FAST)
    # =====================================================
    if provider == "groq":
        if not GROQ_AVAILABLE:
            raise ImportError(
                "langchain-groq not installed. "
                "Run: pip install langchain-groq"
            )

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found.")

        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError(f"Unsupported provider: {provider}")


# =========================================================
# VALIDATION LLM (FAST + CHEAP)
# =========================================================

def get_validation_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
):
    """
    LLM optimized for scoring & validation.
    """
    return get_llm(
        model_name=model_name or os.getenv("VALIDATION_MODEL", "openai/gpt-4o-mini"),
        temperature=0.1,
        provider=provider,
    )


# =========================================================
# REASONING LLM
# =========================================================

def get_reasoning_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
):
    """
    LLM optimized for reasoning & structured thinking.
    """
    return get_llm(
        model_name=model_name or "openai/gpt-4o-mini",
        temperature=0.3,
        provider=provider,
    )


# =========================================================
# CREATIVE LLM
# =========================================================

def get_creative_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
):
    """
    LLM optimized for creative & Feynman-style explanations.
    """
    return get_llm(
        model_name=model_name,
        temperature=0.9,
        provider=provider,
    )
