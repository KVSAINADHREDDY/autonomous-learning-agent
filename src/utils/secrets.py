"""
Secrets management for both local and Streamlit Cloud deployment.
Reads from .env locally and st.secrets on Streamlit Cloud.
"""
import os
from typing import Optional


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a secret value from either environment variables or Streamlit secrets.
    
    Priority:
    1. Environment variable (from .env or system)
    2. Streamlit secrets (for cloud deployment)
    3. Default value
    
    Args:
        key: The secret key to look up
        default: Default value if not found
        
    Returns:
        The secret value or default
    """
    # First try environment variable
    value = os.getenv(key)
    if value:
        return value
    
    # Try Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    
    return default


def load_secrets_to_env():
    """
    Load Streamlit secrets into environment variables.
    Call this at app startup to make secrets available to all modules.
    """
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            for key in st.secrets:
                if key not in os.environ:
                    os.environ[key] = str(st.secrets[key])
    except Exception:
        pass
