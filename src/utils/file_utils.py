import re
import os


def sanitize_filename(name: str) -> str:
    """Sanitize an uploaded filename by keeping the basename and removing unsafe characters.

    This is intentionally conservative: it only keeps alphanumerics, dots, dashes and underscores.
    """
    base = os.path.basename(name)
    # Replace spaces with underscores and strip anything but allowed characters
    sanitized = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    return sanitized