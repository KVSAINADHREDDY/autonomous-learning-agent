"""
LLM provider initialization and configuration.
Supports Hugging Face, Groq, OpenAI, Azure OpenAI, and GitHub Models.
Includes LangSmith integration for observability.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to enable LangSmith tracing
if os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "autonomous-learning-agent")
    print("📊 LangSmith tracing enabled")

# Import LangChain components
from langchain_openai import ChatOpenAI, AzureChatOpenAI

# Optional imports
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from langchain_community.llms import HuggingFaceHub
    from langchain_community.chat_models import ChatHuggingFace
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

try:
    from huggingface_hub import InferenceClient
    HUGGINGFACE_INFERENCE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_INFERENCE_AVAILABLE = False


class HuggingFaceLLM:
    """
    Custom Hugging Face LLM wrapper using Inference API.
    Provides a simple interface for text generation.
    """
    
    def __init__(
        self,
        model_id: str = "mistralai/Mixtral-8x7B-Instruct-v0.1",
        api_key: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        """Initialize Hugging Face LLM."""
        self.model_id = model_id
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not found")
        
        if HUGGINGFACE_INFERENCE_AVAILABLE:
            self.client = InferenceClient(token=self.api_key)
        else:
            self.client = None
            print("⚠️ huggingface_hub not installed")
    
    def invoke(self, prompt: str) -> str:
        """Generate text from prompt."""
        if not self.client:
            return "Error: Hugging Face client not available"
        
        try:
            response = self.client.text_generation(
                prompt,
                model=self.model_id,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True
            )
            return response
        except Exception as e:
            print(f"HuggingFace API error: {e}")
            return f"Error: {str(e)}"
    
    def chat(self, messages: list) -> str:
        """Chat completion with messages."""
        if not self.client:
            return "Error: Hugging Face client not available"
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                model=self.model_id,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback to text generation
            prompt = "\n".join([
                f"{m['role']}: {m['content']}" for m in messages
            ])
            return self.invoke(prompt + "\nassistant:")


# =========================================================
# CORE LLM FACTORY
# =========================================================

def get_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = 1024,
    provider: Optional[str] = None,
):
    """
    Initialize and return an LLM instance.
    
    Supported providers:
    - huggingface (FREE - recommended)
    - groq (FREE tier, fast)
    - github (FREE tier)
    - openai
    - azure
    """
    provider = (provider or os.getenv("MODEL_PROVIDER", "huggingface")).lower()
    
    # =====================================================
    # HUGGING FACE (FREE – RECOMMENDED)
    # =====================================================
    if provider == "huggingface":
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError(
                "HUGGINGFACE_API_KEY not found. "
                "Get one at https://huggingface.co/settings/tokens"
            )
        
        # Use Mixtral or other instruction-tuned model
        model_id = model_name or "mistralai/Mixtral-8x7B-Instruct-v0.1"
        
        return HuggingFaceLLM(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens or 1024
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
            model=model_name or "llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    # =====================================================
    # GITHUB MODELS (FREE)
    # =====================================================
    if provider == "github":
        api_key = os.getenv("GITHUB_TOKEN")
        if not api_key:
            raise ValueError(
                "GITHUB_TOKEN not found. "
                "Create one at https://github.com/settings/tokens"
            )
        
        return ChatOpenAI(
            model=model_name or "gpt-4o-mini",
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
            raise ValueError("OPENAI_API_KEY not found.")
        
        model = model_name or "gpt-4o-mini"
        if model.startswith("openai/"):
            model = model.replace("openai/", "")
        
        return ChatOpenAI(
            model=model,
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
        
        return AzureChatOpenAI(
            azure_deployment=deployment,
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    raise ValueError(f"Unsupported provider: {provider}")


# =========================================================
# SPECIALIZED LLM INSTANCES
# =========================================================

def get_validation_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
):
    """LLM optimized for scoring & validation (low temperature)."""
    return get_llm(
        model_name=model_name,
        temperature=0.1,
        max_tokens=256,
        provider=provider,
    )


def get_reasoning_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
):
    """LLM optimized for reasoning & structured thinking."""
    return get_llm(
        model_name=model_name,
        temperature=0.3,
        max_tokens=1024,
        provider=provider,
    )


def get_creative_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
):
    """LLM optimized for creative & Feynman-style explanations."""
    return get_llm(
        model_name=model_name,
        temperature=0.9,
        max_tokens=2048,
        provider=provider,
    )


def get_quiz_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
):
    """LLM optimized for quiz generation."""
    return get_llm(
        model_name=model_name,
        temperature=0.7,
        max_tokens=2048,
        provider=provider,
    )
