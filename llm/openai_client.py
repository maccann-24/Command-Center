"""
OpenAI API Client

Provides LLM-powered responses for agent chat using GPT-4o.
"""

import os
import logging
from typing import Optional
from openai import OpenAI, APIError, RateLimitError

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Client for OpenAI API.
    
    Handles:
    - API initialization
    - Response generation
    - Rate limiting
    - Error handling
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (gpt-4o, gpt-4o-mini, etc.)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=self.api_key)
        
        logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def generate_response(
        self,
        system_prompt: str,
        conversation_context: str,
        user_message: str,
        max_tokens: int = 300,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate a response using OpenAI.
        
        Args:
            system_prompt: Agent personality and instructions
            conversation_context: Recent conversation history
            user_message: The question/comment to respond to
            max_tokens: Maximum response length
            temperature: Randomness (0.0-1.0)
        
        Returns:
            Generated response text, or None on error
        """
        try:
            # Build full prompt
            full_prompt = self._build_prompt(conversation_context, user_message)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            # Extract response text
            if response.choices and len(response.choices) > 0:
                generated_text = response.choices[0].message.content
                
                # Log token usage
                logger.debug(
                    f"OpenAI response generated. "
                    f"Input tokens: {response.usage.prompt_tokens}, "
                    f"Output tokens: {response.usage.completion_tokens}"
                )
                
                return generated_text.strip()
            else:
                logger.warning("OpenAI returned empty response")
                return None
        
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            return None
        
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {e}", exc_info=True)
            return None
    
    def _build_prompt(self, conversation_context: str, user_message: str) -> str:
        """
        Build the full prompt for OpenAI.
        
        Args:
            conversation_context: Recent chat history
            user_message: Current question/comment
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""Recent conversation:
{conversation_context}

You were just mentioned with this message:
{user_message}

Respond naturally and concisely (under 200 characters). Be helpful and stay in character."""
        
        return prompt
    
    def truncate_response(self, response: str, max_length: int = 200) -> str:
        """
        Truncate response to maximum length.
        
        Ensures responses stay concise for chat.
        
        Args:
            response: Generated response
            max_length: Maximum character length
        
        Returns:
            Truncated response
        """
        if len(response) <= max_length:
            return response
        
        # Truncate at word boundary
        truncated = response[:max_length].rsplit(' ', 1)[0]
        
        # Add ellipsis if truncated
        if len(truncated) < len(response):
            truncated += "..."
        
        return truncated


# Global client instance
_client = None


def get_openai_client() -> OpenAIClient:
    """
    Get or create global OpenAI client.
    
    Returns:
        OpenAIClient instance
    """
    global _client
    
    if _client is None:
        _client = OpenAIClient()
    
    return _client
