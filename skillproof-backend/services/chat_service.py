# Task 11: Chat service — conversational AI grounded in the user's GitHub profile
from typing import Any, Dict, List

from sqlalchemy.orm import Session


class ChatService:
    """Handles multi-turn chat sessions grounded in the user's analysis data.

    Maintains message history in the ChatMessage table and prepends a system
    prompt that includes the user's TPR score, breakdown, flags, and target
    role context so the LLM can give personalised, evidence-based responses.
    """

    def send_message(
        self,
        db: Session,
        user_id: int,
        message: str,
        target_role_id: int | None,
    ) -> str:
        """Process a user message and return the assistant's response.

        Retrieves recent chat history, builds a grounded system prompt, calls
        the LLM, persists both the user message and assistant reply, and
        returns the assistant text.

        Args:
            db:             Active SQLAlchemy session.
            user_id:        Primary key of the User.
            message:        The user's message text.
            target_role_id: Optional target role for context grounding.

        Returns:
            Assistant response text.
        """
        pass

    def get_history(
        self,
        db: Session,
        user_id: int,
        target_role_id: int | None,
        limit: int = 50,
    ) -> List[Any]:
        """Return recent chat messages for a user (and optional target role).

        Args:
            db:             Active SQLAlchemy session.
            user_id:        Primary key of the User.
            target_role_id: Optional filter by target role.
            limit:          Maximum number of messages to return.

        Returns:
            List of ChatMessage ORM instances ordered by created_at ascending.
        """
        pass

    def clear_history(self, db: Session, user_id: int, target_role_id: int | None) -> None:
        """Delete all chat messages for a user (and optional target role).

        Args:
            db:             Active SQLAlchemy session.
            user_id:        Primary key of the User.
            target_role_id: Optional filter by target role.
        """
        pass

    def _build_system_prompt(
        self,
        analysis: Dict[str, Any] | None,
        target_role: Any | None,
    ) -> str:
        """Compose the grounded system prompt from analysis and role data.

        Args:
            analysis:    Latest Analysis ORM instance (or None).
            target_role: TargetRole ORM instance (or None).

        Returns:
            System prompt string to pass to the LLM.
        """
        pass
