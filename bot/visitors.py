"""Сколько людей писали боту. Хранятся только id и даты, без имён и текста."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from aiogram import BaseMiddleware

from bot.storage import data_dir

# Москва без перехода на летнее время.
_ZONE = timezone(timedelta(hours=3))
_VISITORS = "visitors.txt"
_OWNER = "owner.txt"


def record_visit(user_id: int, moment: datetime | None = None) -> None:
    now = moment.astimezone(_ZONE) if moment is not None else datetime.now(_ZONE)
    day = now.date().isoformat()
    rows = _read_visitors()
    first, _last = rows.get(user_id, (day, day))
    rows[user_id] = (first, day)
    _write_visitors(rows)


def stats_text(today: date | None = None) -> str:
    current = today or datetime.now(_ZONE).date()
    mark = current.isoformat()
    rows = _read_visitors()
    new_today = sum(1 for first, _last in rows.values() if first == mark)
    active_today = sum(1 for _first, last in rows.values() if last == mark)
    return (
        "Пользователи бота\n"
        f"Всего: {len(rows)}\n"
        f"Новых сегодня: {new_today}\n"
        f"Писали сегодня: {active_today}"
    )


def allow_stats(user_id: int) -> bool:
    """Первый, кто вызвал /stats, видит цифры. Остальным команда недоступна."""
    path = data_dir() / _OWNER
    if not path.is_file():
        path.write_text(f"{user_id}\n", encoding="utf-8")
        return True
    owners = {
        int(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().isdigit()
    }
    return user_id in owners


class RememberVisitor(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if user is not None and not getattr(user, "is_bot", False):
            record_visit(user.id)
        return await handler(event, data)


def _read_visitors() -> dict[int, tuple[str, str]]:
    path = data_dir() / _VISITORS
    if not path.is_file():
        return {}
    rows: dict[int, tuple[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        rows[int(parts[0])] = (parts[1], parts[2])
    return rows


def _write_visitors(rows: dict[int, tuple[str, str]]) -> None:
    path = data_dir() / _VISITORS
    body = "".join(f"{user_id} {first} {last}\n" for user_id, (first, last) in sorted(rows.items()))
    temporary = path.with_suffix(".tmp")
    temporary.write_text(body, encoding="utf-8")
    temporary.replace(path)
