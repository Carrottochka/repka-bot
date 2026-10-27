"""Папка, которая переживает пересборку на Amvera."""

from __future__ import annotations

import os
from pathlib import Path

_LOCAL_DATA = Path(__file__).resolve().parent.parent / "data"
_AMVERA_DATA = Path("/data")


def data_dir() -> Path:
    override = os.getenv("REPKA_DATA_DIR", "").strip()
    if override:
        path = Path(override)
    elif os.name != "nt" and _AMVERA_DATA.is_dir():
        path = _AMVERA_DATA
    else:
        path = _LOCAL_DATA
    path.mkdir(parents=True, exist_ok=True)
    return path
