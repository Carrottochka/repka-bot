import os
from pathlib import Path


def _load_env(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env(Path(__file__).resolve().parent.parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

RUSTORE_URL = "https://www.rustore.ru/catalog/app/com.example.repka_crop"
DEVELOPER_EMAIL = "repka-crop@yandex.ru"
