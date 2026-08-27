# Task 11: LLM generator — centralised wrapper around Google Gemini API
from typing import Any, Dict, Optional


class LLMGenerator:
    """Centralised wrapper for all LLM calls in SkillProof.

    Handles model selection, fallback on quota errors, mock mode for
    development (USE_LLM_MOCK=true), and prompt templating.
    """

    def __init__(self) -> None:
        """Initialise the Gemini client and configure mock mode from settings."""
        pass

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Send a prompt to the configured Gemini model and return the response text.

        Automatically falls back to GEMINI_FALLBACK_MODEL on quota errors.
        Returns a hard-coded mock string when USE_LLM_MOCK is True.

        Args:
            prompt:             The user-facing prompt content.
            system_instruction: Optional system-level instruction to prepend.

        Returns:
            Raw LLM response text string.
        """
        pass

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Like :meth:`generate` but parses and returns the response as a dict.

        Strips markdown code fences (```json ... ```) if present before parsing.

        Args:
            prompt:             The prompt requesting a JSON response.
            system_instruction: Optional system instruction.

        Returns:
            Parsed dict from the LLM's JSON response.

        Raises:
            ValueError: If the LLM response cannot be parsed as valid JSON.
        """
        pass

    def _mock_response(self, prompt: str) -> str:
        """Return a deterministic mock response for development/testing.

        Args:
            prompt: The original prompt (used to vary mock output by type).

        Returns:
            A JSON-safe placeholder string.
        """
        pass
