# Task 9: LLM generator — centralised wrapper around Google Gemini API
"""
Single entry point for all LLM calls in SkillProof.

Features:
- Mock mode (USE_LLM_MOCK=true) returns deterministic JSON-safe responses
  without calling the API — preserves quota during development.
- Primary model: GEMINI_MODEL (gemini-3.7-flash)
- Fallback model: GEMINI_FALLBACK_MODEL on quota/rate-limit errors
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
    """Centralised wrapper for all Gemini API calls."""

    def __init__(self) -> None:
        self._primary_model = None
        self._fallback_model = None
        if not settings.USE_LLM_MOCK:
            self._init_gemini()

    def _init_gemini(self) -> None:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._primary_model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self._fallback_model = genai.GenerativeModel(settings.GEMINI_FALLBACK_MODEL)
            logger.info("Gemini initialised — primary: %s", settings.GEMINI_MODEL)
        except Exception as exc:
            logger.warning("Failed to initialise Gemini: %s", exc)

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> LLMResult:
        """Send a prompt and return an LLMResult with the response text."""
        if settings.USE_LLM_MOCK:
            return LLMResult(success=True, text=self._mock_response(prompt))

        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

        for model, label in [(self._primary_model, "primary"), (self._fallback_model, "fallback")]:
            if model is None:
                continue
            try:
                response = model.generate_content(full_prompt)
                return LLMResult(success=True, text=response.text)
            except Exception as exc:
                exc_str = str(exc).lower()
                if "quota" in exc_str or "429" in exc_str or "resource_exhausted" in exc_str:
                    logger.warning("Quota exceeded on %s model, trying fallback", label)
                    if label == "fallback":
                        return LLMResult(
                            success=False,
                            error_type="quota_exceeded",
                            error_message="Both Gemini models are quota-limited. Try again later.",
                        )
                    time.sleep(2)
                    continue
                logger.error("Gemini %s model error: %s", label, exc)
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

    def _mock_response(self, prompt: str) -> str:
        """Return a plain-text mock response based on prompt type."""
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
        """Return a JSON-safe mock response matching expected schema by prompt type."""
        prompt_lower = prompt.lower()

        if "skeptic" in prompt_lower or "advocate" in prompt_lower or "synthesize" in prompt_lower or "verdict" in prompt_lower:
            return json.dumps({
                "final_verdict": "Mock verdict: Candidate shows moderate readiness with clear areas for growth.",
                "confidence": 55,
                "surviving_skeptic_points": ["Limited PR activity", "Sparse commit history"],
                "surviving_advocate_points": ["Multi-language experience", "Active recent commits"],
            })

        if "scenario" in prompt_lower or "question" in prompt_lower or "task" in prompt_lower:
            return json.dumps({
                "target_repo": "mock-repo",
                "scenario": "Describe how you approached error handling in one of your Python projects.",
                "what_a_strong_answer_shows": "Understanding of exception hierarchies, logging, and graceful degradation.",
                "difficulty": "medium",
            })

        if "quality_score" in prompt_lower or "evaluate" in prompt_lower or "answer" in prompt_lower:
            return json.dumps({
                "quality_score": 65,
                "reasoning": "Mock evaluation: Answer demonstrates basic understanding but lacks specific examples.",
                "pass_fail": "pass",
            })

        if "matched_requirements" in prompt_lower or "gap" in prompt_lower or "jd" in prompt_lower or "job description" in prompt_lower:
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

        if "task" in prompt_lower or "missing" in prompt_lower or "verification" in prompt_lower:
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
