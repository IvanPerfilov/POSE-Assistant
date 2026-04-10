from __future__ import annotations


def normalize_username(username: str | None) -> str:
    if not username:
        return "без username"
    if username.startswith("@"):
        return username
    return f"@{username}"
