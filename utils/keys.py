import os
from typing import Optional

def get_openai_key() -> str:
    """Get OpenAI API key from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it with your OpenAI API key."
        )
    return api_key

def get_anthropic_key() -> Optional[str]:
    """Get Anthropic API key from environment variables."""
    return os.getenv("ANTHROPIC_API_KEY")

# For backward compatibility
openai_key = get_openai_key()
