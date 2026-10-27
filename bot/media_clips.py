"""Короткие ролики к урокам: media/guide/<id>.mp4 и соседние форматы."""

from __future__ import annotations

from pathlib import Path

MEDIA_DIR = Path(__file__).resolve().parent.parent / "media" / "guide"
_SUFFIXES = (".mp4", ".mov", ".webm", ".mkv")


def clip_path(lesson_id: str) -> Path | None:
    if not MEDIA_DIR.is_dir():
        return None
    for suffix in _SUFFIXES:
        path = MEDIA_DIR / f"{lesson_id}{suffix}"
        if path.is_file() and path.stat().st_size > 0:
            return path
    return None


def clip_destination(lesson_id: str, suffix: str) -> Path:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    safe_suffix = suffix if suffix.startswith(".") else f".{suffix}"
    if safe_suffix.lower() not in _SUFFIXES:
        safe_suffix = ".mp4"
    for old_suffix in _SUFFIXES:
        old = MEDIA_DIR / f"{lesson_id}{old_suffix}"
        if old.is_file() and old.suffix.lower() != safe_suffix.lower():
            old.unlink()
    return MEDIA_DIR / f"{lesson_id}{safe_suffix.lower()}"
