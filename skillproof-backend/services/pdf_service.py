# Task 15: PDF service — generates styled PDF verification reports
"""
Generates a downloadable PDF using WeasyPrint from an inline HTML template.
No external CSS or font files — fully self-contained for Render deployment.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class PDFService:
    """Generates downloadable PDF verification reports."""

    def generate_report(self, report_data: Dict[str, Any]) -> bytes:
        """Render a PDF from report_data and return raw bytes."""
        html = self.build_html(report_data)
        try:
            from weasyprint import HTML
            return HTML(string=html).write_pdf()
        except Exception as exc:
            logger.error("WeasyPrint PDF generation failed: %s", exc)
            raise

    def build_html(self, report_data: Dict[str, Any]) -> str:
        """Build the full HTML string for the PDF report."""
        user = report_data.get("user", {})
        analysis = report_data.get("analysis", {})
        target_role = report_data.get("target_role")
        verdict = report_data.get("verdict")
        tasks = report_data.get("tasks", [])
        milestones = report_data.get("milestones", [])
        generated_at = datetime.now().strftime("%B %d, %Y")

        tpr_score = analysis.get("tpr_score", 0)
        lr_score = analysis.get("lr_score")
        confidence = analysis.get("confidence_level", "unknown")
        breakdown = analysis.get("breakdown", {})
        flags = analysis.get("flags", {})
        green_flags = flags.get("green_flags", [])
        red_flags = flags.get("red_flags", [])

        candidate_name = user.get("full_name") or user.get("github_username", "Unknown")
        github_username = user.get("github_username", "")
        headline = user.get("profile_headline", "") or ""

        if tpr_score >= 65:
            tier = "Strong"
            tier_color = "#22c55e"
        elif tpr_score >= 35:
            tier = "Developing"
            tier_color = "#f59e0b"
        else:
            tier = "Early Stage"
            tier_color = "#ef4444"

        def _score(key: str) -> float:
            val = breakdown.get(key, {})
            return float(val.get("raw_score", 0)) if isinstance(val, dict) else 0.0

        breakdown_rows = "".join(
            f"<tr><td>{label}</td><td>{_score(key):.0f}/100</td>"
            f"<td><div class='bar' style='width:{_score(key):.0f}%; background:{color}'></div></td></tr>"
            for key, label, color in [
                ("commit_quality",   "Commit Quality",   "#6366f1"),
                ("pr_collaboration", "PR Collaboration",  "#8b5cf6"),
                ("code_review",      "Code Review",       "#06b6d4"),
                ("consistency",      "Consistency",       "#10b981"),
                ("repo_depth",       "Repo Depth",        "#f59e0b"),
            ]
        )

        green_items = "".join(f"<li>{f}</li>" for f in green_flags) or "<li>None identified</li>"
        red_items = "".join(f"<li>{f}</li>" for f in red_flags) or "<li>None identified</li>"

        role_section = ""
        if target_role:
            readiness = target_role.get("readiness_score", 0) or 0
            company = f" at {target_role.get('company_name')}" if target_role.get("company_name") else ""
            role_section = f"""
            <div class="section">
                <h2>Target Role: {target_role.get('role_title', '')}{company}</h2>
                <p class="readiness">Readiness Estimate: <strong>{readiness}%</strong></p>
            </div>"""

        verdict_section = ""
        if verdict and verdict.get("final_verdict"):
            conf = verdict.get("confidence", 0) or 0
            verdict_section = f"""
            <div class="section">
                <h2>Expert Panel Review</h2>
                <p>{verdict['final_verdict']}</p>
                <p class="meta">Panel confidence: {conf:.0f}%</p>
            </div>"""

        completed = [t for t in tasks if t.get("status") == "verified_complete"]
        tasks_section = ""
        if completed:
            task_rows = "".join(
                f"<tr><td>{t.get('missing_requirement', '')}</td>"
                f"<td>{t.get('target_repo', '')}</td>"
                f"<td>Verified</td></tr>"
                for t in completed
            )
            tasks_section = f"""
            <div class="section">
                <h2>Completed Improvement Tasks</h2>
                <table><tr><th>Requirement</th><th>Repo</th><th>Status</th></tr>
                {task_rows}</table>
            </div>"""

        milestone_badges = "".join(
            f"<span class='badge'>{m.get('label', '')}</span>"
            for m in milestones
        )
        milestones_section = f"""
        <div class="section">
            <h2>Earned Badges</h2>
            <div class="badges">{milestone_badges or '<span>No badges yet</span>'}</div>
        </div>"""

        lr_section = ""
        if lr_score is not None:
            lr_section = f"<p class='meta'>LR Model Score: {lr_score:.1f}/100</p>"

        gh_link = f"github.com/{github_username}" if github_username else ""
        at_handle = f'<span class="meta"> · @{github_username}</span>' if github_username else ""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; color: #1f2937; font-size: 13px; }}
  h1 {{ color: #4f46e5; font-size: 24px; margin-bottom: 4px; }}
  h2 {{ color: #374151; font-size: 16px; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; margin-top: 24px; }}
  .header {{ display: flex; justify-content: space-between; align-items: flex-start; }}
  .score-block {{ text-align: center; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px 24px; }}
  .score-big {{ font-size: 48px; font-weight: bold; color: #4f46e5; line-height: 1; }}
  .tier {{ font-size: 14px; font-weight: bold; color: {tier_color}; }}
  .section {{ margin-top: 20px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
  th, td {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid #f3f4f6; }}
  th {{ background: #f9fafb; font-weight: bold; color: #6b7280; font-size: 11px; text-transform: uppercase; }}
  .bar-cell {{ width: 40%; }}
  .bar {{ height: 10px; border-radius: 4px; min-width: 2px; }}
  ul {{ margin: 8px 0; padding-left: 20px; }}
  li {{ margin: 4px 0; }}
  .green {{ color: #059669; }}
  .red {{ color: #dc2626; }}
  .meta {{ color: #6b7280; font-size: 11px; }}
  .readiness {{ font-size: 16px; }}
  .badges {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }}
  .badge {{ background: #ede9fe; color: #5b21b6; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; }}
  .footer {{ margin-top: 40px; border-top: 1px solid #e5e7eb; padding-top: 12px; color: #9ca3af; font-size: 10px; text-align: center; }}
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>SkillProof Verification Report</h1>
      <p style="color:#6b7280;margin:0">{headline}</p>
      <p style="margin:4px 0"><strong>{candidate_name}</strong>{at_handle}</p>
      <p class="meta">Generated {generated_at}</p>
    </div>
    <div class="score-block">
      <div class="score-big">{tpr_score:.0f}</div>
      <div style="color:#6b7280;font-size:11px">TPR Score / 100</div>
      <div class="tier">{tier}</div>
      <div class="meta">Confidence: {confidence}</div>
      {lr_section}
    </div>
  </div>

  <div class="section">
    <h2>Score Breakdown</h2>
    <table>
      <tr><th>Dimension</th><th>Score</th><th class="bar-cell">Visual</th></tr>
      {breakdown_rows}
    </table>
  </div>

  <div class="section">
    <h2>Strengths and Areas to Improve</h2>
    <div style="display:flex;gap:32px">
      <div style="flex:1">
        <strong class="green">Strengths</strong>
        <ul class="green">{green_items}</ul>
      </div>
      <div style="flex:1">
        <strong class="red">Areas to Improve</strong>
        <ul class="red">{red_items}</ul>
      </div>
    </div>
  </div>

  {role_section}
  {verdict_section}
  {tasks_section}
  {milestones_section}

  <div class="footer">
    Generated by SkillProof · Evidence-grounded developer verification · {gh_link}
  </div>
</body>
</html>"""

    def assemble_report_data(
        self,
        db: Session,
        user_id: int,
        target_role_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Fetch all required data from the database."""
        from models.database import (
            Analysis, EvaluationVerdict, Milestone, Task, TargetRole, User,
        )

        user = db.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        analysis = (
            db.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
            .first()
        )

        target_role_data = None
        verdict_data = None
        tasks: List[Any] = []

        if target_role_id:
            role = db.get(TargetRole, target_role_id)
            if role:
                target_role_data = {
                    "role_title": role.role_title,
                    "company_name": role.company_name,
                    "readiness_score": role.latest_readiness_score,
                }
                verdict = (
                    db.query(EvaluationVerdict)
                    .filter(
                        EvaluationVerdict.target_role_id == target_role_id,
                        EvaluationVerdict.user_id == user_id,
                    )
                    .order_by(EvaluationVerdict.created_at.desc())
                    .first()
                )
                if verdict:
                    verdict_data = {
                        "final_verdict": verdict.final_verdict,
                        "confidence": verdict.confidence,
                    }
                tasks = (
                    db.query(Task)
                    .filter(
                        Task.user_id == user_id,
                        Task.target_role_id == target_role_id,
                    )
                    .order_by(Task.created_at.desc())
                    .all()
                )

        milestones = db.query(Milestone).filter(Milestone.user_id == user_id).all()

        return {
            "user": {
                "full_name": user.full_name,
                "github_username": user.github_username,
                "profile_headline": user.profile_headline,
            },
            "analysis": {
                "tpr_score": analysis.tpr_score if analysis else 0,
                "lr_score": analysis.lr_score if analysis else None,
                "confidence_level": analysis.confidence_level if analysis else "low",
                "breakdown": analysis.breakdown if analysis else {},
                "flags": analysis.flags if analysis else {},
            },
            "target_role": target_role_data,
            "verdict": verdict_data,
            "tasks": [
                {
                    "missing_requirement": t.missing_requirement,
                    "target_repo": t.target_repo,
                    "status": t.status,
                }
                for t in tasks
            ],
            "milestones": [
                {"label": m.milestone_label, "key": m.milestone_key}
                for m in milestones
            ],
        }
