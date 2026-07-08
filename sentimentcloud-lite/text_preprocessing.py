import re

import emoji


def preprocess_text(text: object) -> str:
    """Membersihkan komentar Bahasa Indonesia dengan aturan sederhana."""
    if text is None:
        return ""

    cleaned = str(text).lower()
    cleaned = re.sub(r"https?://\S+|www\.\S+", " ", cleaned)
    cleaned = re.sub(r"@\w+", " ", cleaned)
    cleaned = cleaned.replace("#", "")
    cleaned = emoji.replace_emoji(cleaned, replace=" ")
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", cleaned)
    cleaned = re.sub(r"([a-zA-Z])\1{2,}", r"\1", cleaned)
    cleaned = re.sub(r"([a-zA-Z])\1\b", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
