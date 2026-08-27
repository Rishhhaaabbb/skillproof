# Task 10: JD analyzer — parses job descriptions and extracts structured requirements
from typing import Any, Dict, List


class JDAnalyzer:
    """Extracts structured requirements from raw job description text.

    Uses the LLM (via LLMGenerator) to identify required skills, experience
    levels, and responsibility themes.  Output feeds into readiness scoring
    and gap analysis.
    """

    def analyze(self, jd_text: str) -> Dict[str, Any]:
        """Parse a job description into structured requirements.

        Args:
            jd_text: Cleaned job description text (output of clean_jd_text).

        Returns:
            Dict with:
              - 'required_skills': list of skill strings
              - 'preferred_skills': list of skill strings
              - 'experience_years': int or None
              - 'seniority_level': 'junior' | 'mid' | 'senior' | 'staff' | None
              - 'key_responsibilities': list of strings
              - 'tech_stack': list of technology strings
        """
        pass

    def compute_readiness_score(
        self,
        jd_requirements: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> float:
        """Score how ready the candidate is for the role based on their analysis.

        Args:
            jd_requirements: Structured requirements from :meth:`analyze`.
            analysis:        Latest analysis dict (features, breakdown, flags).

        Returns:
            Readiness score as a float in [0, 100].
        """
        pass

    def compute_gap_analysis(
        self,
        jd_requirements: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Identify gaps between the candidate's profile and the JD requirements.

        Args:
            jd_requirements: Structured requirements from :meth:`analyze`.
            analysis:        Latest analysis dict.

        Returns:
            Dict with:
              - 'matched_skills': list of skills the candidate demonstrates
              - 'missing_skills': list of skills absent from the profile
              - 'gap_description': human-readable summary string
              - 'top_priorities': list of the most impactful gaps to address
        """
        pass

    def extract_skill_tags(self, jd_requirements: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate SkillTag records from JD requirements cross-referenced with analysis.

        Args:
            jd_requirements: Structured requirements from :meth:`analyze`.
            analysis:        Latest analysis dict.

        Returns:
            List of dicts, each with 'tag', 'confidence', and 'source'.
        """
        pass
