"""Кто может прикладывать ролики к урокам."""

from __future__ import annotations

from bot.storage import data_dir

def _admins_path():
    return data_dir() / "admins.txt"


def _read_ids() -> set[int]:
    path = _admins_path()
    if not path.is_file():
        return set()
    ids: set[int] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.isdigit():
            ids.add(int(line))
    return ids


def is_admin(user_id: int) -> bool:
    return user_id in _read_ids()


def claim_admin(user_id: int) -> bool:
    """Первый, кто прислал ролик, становится редактором инструкции."""
    ids = _read_ids()
    if ids:
        return user_id in ids
    path = _admins_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{user_id}\n", encoding="utf-8")
    return True
