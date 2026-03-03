"""
Anthropic Claude API Client

Provides LLM-powered responses for agent chat using Claude 3.5 Sonnet.
"""

import os
import logging
from typing import Optional
from anthropic import Anthropic, APIError, RateLimitError

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Client for Anthropic Claude API.
    
    Handles:
    - API initialization
    - Response generation
    - Rate limiting
    - Error handling
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5"):
        """
        Initialize Claude client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = Anthropic(api_key=self.api_key)
        
        logger.info(f"Claude client initialized with model: {self.model}")
    
    def generate_response(
        self,
        system_prompt: str,
        conversation_context: str,
        user_message: str,
        max_tokens: int = 300,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate a response using Claude.
        
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
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            # Extract response text
            if response.content and len(response.content) > 0:
                generated_text = response.content[0].text
                
                # Log token usage
                logger.debug(
                    f"Claude response generated. "
                    f"Input tokens: {response.usage.input_tokens}, "
                    f"Output tokens: {response.usage.output_tokens}"
                )
                
                return generated_text.strip()
            else:
                logger.warning("Claude returned empty response")
                return None
        
        except RateLimitError as e:
            logger.error(f"Claude rate limit exceeded: {e}")
            return None
        
        except APIError as e:
            logger.error(f"Claude API error: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error calling Claude: {e}", exc_info=True)
            return None
    
    def _build_prompt(self, conversation_context: str, user_message: str) -> str:
        """
        Build the full prompt for Claude.
        
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


def get_claude_client() -> ClaudeClient:
    """
    Get or create global Claude client.
    
    Returns:
        ClaudeClient instance
    """
    global _client
    
    if _client is None:
        _client = ClaudeClient()
    
    return _client
