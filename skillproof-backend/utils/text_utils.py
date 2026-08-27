# Task 1: Text cleaning and normalisation utilities
import re
from html.parser import HTMLParser


# ---------------------------------------------------------------------------
# HTML stripper
# ---------------------------------------------------------------------------


class _HTMLStripper(HTMLParser):
    """Minimal HTML parser that collects visible text nodes."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts)


def strip_html(text: str) -> str:
    """Remove all HTML tags from *text* and return plain text.

    Non-HTML strings are returned unchanged.

    Args:
        text: Raw string that may contain HTML markup.

    Returns:
        Plain text with tags removed.
    """
    if not text:
        return text
    stripper = _HTMLStripper()
    stripper.feed(text)
    return stripper.get_text()


# ---------------------------------------------------------------------------
# Whitespace normalisation
# ---------------------------------------------------------------------------


def normalize_whitespace(text: str) -> str:
    """Collapse consecutive whitespace characters into a single space and strip
    leading/trailing whitespace.

    Args:
        text: Input string.

    Returns:
        Normalised string.
    """
    if not text:
        return text
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Truncation
# ---------------------------------------------------------------------------


def truncate_text(text: str, max_chars: int = 5000) -> str:
    """Return at most *max_chars* characters of *text*, appending ``…`` when
    truncation occurs.

    Args:
        text:      Input string.
        max_chars: Maximum allowed character count.  Defaults to 5000.

    Returns:
        Possibly truncated string.
    """
    if not text or len(text) <= max_chars:
        return text
    return text[:max_chars] + "…"


# ---------------------------------------------------------------------------
# Composite cleaner for job descriptions
# ---------------------------------------------------------------------------


def clean_jd_text(raw: str, max_chars: int = 5000) -> str:
    """Clean a raw job description string by composing all three utilities.

    Pipeline: strip_html → normalize_whitespace → truncate_text

    Args:
        raw:       Raw job description (may contain HTML, excessive whitespace).
        max_chars: Maximum character count after cleaning.  Defaults to 5000.

    Returns:
        Clean, normalised, truncated string ready for LLM / embedding use.
    """
    text = strip_html(raw)
    text = normalize_whitespace(text)
    text = truncate_text(text, max_chars=max_chars)
    return text
