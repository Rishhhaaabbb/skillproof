# Task 15: PDF service — generates a styled PDF report from analysis data
from typing import Any, Dict


class PDFService:
    """Generates a downloadable PDF verification report for a candidate.

    Uses WeasyPrint to render an HTML template into a PDF byte stream.
    The report includes the TPR score, LR score, breakdown chart data,
    skills, flags, target role readiness, and the evaluation verdict.
    """

    def generate_report(self, report_data: Dict[str, Any]) -> bytes:
        """Render a PDF report from the provided report data.

        Args:
            report_data: Dict containing:
              - 'user': dict with full_name, github_username, profile_headline
              - 'analysis': dict with tpr_score, lr_score, breakdown, flags
              - 'target_role': dict with role_title, company_name, readiness_score
              - 'verdict': dict with final_verdict, confidence
              - 'tasks': list of completed task dicts
              - 'milestones': list of earned milestone dicts

        Returns:
            Raw PDF bytes ready to serve as a file download.
        """
        pass

    def build_html(self, report_data: Dict[str, Any]) -> str:
        """Render the Jinja2/f-string HTML template for the PDF.

        Args:
            report_data: Same dict as :meth:`generate_report`.

        Returns:
            Full HTML string.
        """
        pass

    def assemble_report_data(self, db: Any, user_id: int, target_role_id: int) -> Dict[str, Any]:
        """Fetch all required data from the database to build the report.

        Args:
            db:             Active SQLAlchemy session.
            user_id:        Primary key of the User.
            target_role_id: Primary key of the TargetRole.

        Returns:
            Assembled report_data dict ready for :meth:`generate_report`.
        """
        pass
