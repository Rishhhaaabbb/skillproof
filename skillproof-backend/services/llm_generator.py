# Task 9: LLM generator — centralised wrapper around Google Gemini API
"""
Single entry point for all LLM calls in SkillProof.

Features:
- Mock mode (USE_LLM_MOCK=true) returns deterministic JSON-safe responses
  without calling the API — preserves quota during development.
- Primary model: GEMINI_MODEL (gemini-2.5-flash)
- Fallback model: GEMINI_FALLBACK_MODEL on quota/rate-limit errors
- Uses google-genai SDK (v2+), replacing deprecated google-generativeai
- All JSON responses strip markdown fences before parsing
- Structured error types: quota_exceeded, invalid_json, unavailable
"""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict, Optional

from config import settings

logger = logging.getLogger(__name__)

# Regex to strip ```json ... ``` or ``` ... ``` fences
_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL)


class LLMResult:
    """Typed result wrapper for all LLM calls."""

    def __init__(
        self,
        success: bool,
        text: str = "",
        data: Optional[Dict[str, Any]] = None,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        self.success = success
        self.text = text
        self.data = data
        self.error_type = error_type  # 'quota_exceeded' | 'invalid_json' | 'unavailable' | None
        self.error_message = error_message


class LLMGenerator:
    """Centralised wrapper for all Gemini API calls using google-genai SDK."""

    def __init__(self) -> None:
        self._client = None
        if not settings.USE_LLM_MOCK:
            self._init_gemini()

    def _init_gemini(self) -> None:
        try:
            from google import genai
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            logger.info("Gemini initialised — primary: %s", settings.GEMINI_MODEL)
        except Exception as exc:
            logger.warning("Failed to initialise Gemini: %s", exc)

    def _call_model(self, model_name: str, prompt: str) -> str:
        """Call a specific model and return the response text. Raises on error."""
        from google.genai import types as genai_types
        response = self._client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=2048,
            ),
        )
        return response.text

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> LLMResult:
        """Send a prompt and return an LLMResult with the response text."""
        if settings.USE_LLM_MOCK:
            return LLMResult(success=True, text=self._mock_response(prompt))

        if self._client is None:
            return LLMResult(
                success=False,
                error_type="unavailable",
                error_message="Gemini client not initialised — check GEMINI_API_KEY.",
            )

        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

        models = [settings.GEMINI_MODEL, settings.GEMINI_FALLBACK_MODEL]
        for i, model_name in enumerate(models):
            label = "primary" if i == 0 else "fallback"
            try:
                text = self._call_model(model_name, full_prompt)
                return LLMResult(success=True, text=text)
            except Exception as exc:
                exc_str = str(exc).lower()
                if any(k in exc_str for k in ("quota", "429", "resource_exhausted")):
                    logger.warning("Quota exceeded on %s model (%s), trying fallback", label, model_name)
                    if label == "fallback":
                        return LLMResult(
                            success=False,
                            error_type="quota_exceeded",
                            error_message="Both Gemini models are quota-limited. Try again later.",
                        )
                    time.sleep(5)  # wait 5s before trying fallback
                    continue
                logger.error("Gemini %s model error (%s): %s", label, model_name, exc)
                return LLMResult(
                    success=False,
                    error_type="unavailable",
                    error_message=str(exc),
                )

        return LLMResult(success=False, error_type="unavailable", error_message="No models available")

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> LLMResult:
        """Like generate() but parses and returns the response as a dict in .data."""
        if settings.USE_LLM_MOCK:
            mock_text = self._mock_json_response(prompt)
            try:
                return LLMResult(success=True, text=mock_text, data=json.loads(mock_text))
            except json.JSONDecodeError:
                return LLMResult(success=True, text=mock_text, data={})

        result = self.generate(prompt, system_instruction)
        if not result.success:
            return result

        text = result.text.strip()
        match = _FENCE_RE.match(text)
        if match:
            text = match.group(1).strip()

        try:
            data = json.loads(text)
            return LLMResult(success=True, text=text, data=data)
        except json.JSONDecodeError as exc:
            logger.warning("LLM returned invalid JSON: %s\nRaw: %s", exc, text[:200])
            return LLMResult(
                success=False,
                text=text,
                error_type="invalid_json",
                error_message=f"Could not parse LLM response as JSON: {exc}",
            )

    # -------------------------------------------------------------------------
    # Mock helpers
    # -------------------------------------------------------------------------

    def _mock_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "skeptic" in prompt_lower:
            return "Mock skeptic case: The candidate shows limited PR activity and sparse commit history, suggesting they may not yet be production-ready for this role."
        if "advocate" in prompt_lower:
            return "Mock advocate case: The candidate demonstrates multi-language experience and consistent commit patterns, showing genuine development engagement."
        if "scenario" in prompt_lower or "interview" in prompt_lower:
            return "Mock scenario: Based on your Python repos, describe how you would structure a REST API with proper error handling."
        if "summary" in prompt_lower or "executive" in prompt_lower:
            return "Mock summary: Your TPR score reflects solid foundational skills with room to grow in collaborative practices like code reviews and pull requests."
        return "Mock LLM response: Analysis complete. Please enable real LLM mode for production use."

    def _mock_json_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()

        if any(k in prompt_lower for k in ("skeptic", "advocate", "synthesize", "verdict")):
            return json.dumps({
                "final_verdict": "Mock verdict: Candidate shows moderate readiness with clear areas for growth.",
                "confidence": 55,
                "surviving_skeptic_points": ["Limited PR activity", "Sparse commit history"],
                "surviving_advocate_points": ["Multi-language experience", "Active recent commits"],
            })

        if any(k in prompt_lower for k in ("scenario", "question", "task")):
            return json.dumps({
                "target_repo": "mock-repo",
                "scenario": "Describe how you approached error handling in one of your Python projects.",
                "what_a_strong_answer_shows": "Understanding of exception hierarchies, logging, and graceful degradation.",
                "difficulty": "medium",
            })

        if any(k in prompt_lower for k in ("quality_score", "evaluate", "answer")):
            return json.dumps({
                "quality_score": 65,
                "reasoning": "Mock evaluation: Answer demonstrates basic understanding but lacks specific examples.",
                "pass_fail": "pass",
            })

        if any(k in prompt_lower for k in ("matched_requirements", "gap", "jd", "job description")):
            return json.dumps({
                "matched_requirements": [
                    {"requirement": "Python development", "evidence_citation": "mock-python-repo"}
                ],
                "missing_requirements": ["System design experience", "CI/CD pipeline setup"],
                "recommended_actions": [
                    "Add a CI/CD workflow to one of your repos",
                    "Write a system design document for an existing project",
                ],
                "readiness_estimate": 45,
            })

        if any(k in prompt_lower for k in ("task", "missing", "verification")):
            return json.dumps({
                "target_repo": "mock-repo",
                "task_description": "Add unit tests covering at least 3 core functions in your main module.",
                "verification_signal": {
                    "file_pattern": "test_*.py",
                    "keyword": "assert",
                    "repo": "mock-repo",
                },
            })

        if "chat" in prompt_lower:
            return json.dumps({"answer": "Mock chat response: Focus on improving your PR collaboration score."})

        return json.dumps({"result": "mock", "message": "Mock JSON response"})
