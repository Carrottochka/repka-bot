"""Справочник совместимых культур.

Повторяет CompanionPlantsLookup из приложения: те же записи и то же
сопоставление по вхождению названия.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class _Entry:
    keys: tuple[str, ...]
    neighbors: tuple[str, ...]


_ENTRIES = (
    _Entry(("фасоль вьющаяся",), ("кукуруза", "тыква", "подсолнечник")),
    _Entry(
        ("фасоль кустовая",),
        ("картофель", "кукуруза", "сельдерей", "огурец", "свекла", "редис"),
    ),
    _Entry(
        ("капуста белокочанная",),
        (
            "укроп",
            "сельдерей",
            "лук",
            "шалфей",
            "мята",
            "тимьян",
            "розмарин",
            "бархатцы",
            "картофель",
        ),
    ),
    _Entry(("цветная капуста",), ("сельдерей", "укроп", "шалфей", "лук-порей")),
    _Entry(
        ("перец сладкий",),
        ("базилик", "морковь", "лук", "петрушка", "томаты", "бархатцы"),
    ),
    _Entry(
        ("лук репчатый",),
        ("морковь", "свекла", "салат", "огурец", "томат", "чабер", "ромашка"),
    ),
    _Entry(("лук-порей",), ("сельдерей", "морковь", "томат", "клубника")),
    _Entry(("горох",), ("овес", "кукуруза", "морковь", "огурец", "редис", "репа")),
    _Entry(("бобы", "боб"), ("картофель", "капуста", "морковь", "свекла", "огурец")),
    _Entry(
        ("томат", "помидор", "помидоры", "томаты"),
        ("базилик", "бархатцы", "чеснок", "лук", "морковь", "петрушка", "спаржа", "настурция"),
    ),
    _Entry(("перец",), ("базилик", "морковь", "лук", "петрушка", "томаты", "бархатцы")),
    _Entry(("баклажан",), ("фасоль кустовая", "перец", "чабер", "бархатцы", "шпинат")),
    _Entry(
        ("картофель", "картошка"),
        ("фасоль", "кукуруза", "капуста", "хрен", "бархатцы", "баклажан", "чеснок"),
    ),
    _Entry(
        ("капуста",),
        (
            "укроп",
            "сельдерей",
            "лук",
            "шалфей",
            "мята",
            "тимьян",
            "розмарин",
            "бархатцы",
            "картофель",
        ),
    ),
    _Entry(("брокколи",), ("сельдерей", "лук", "шалфей", "свекла", "картофель")),
    _Entry(("редис",), ("морковь", "огурец", "салат", "шпинат", "горох", "настурция")),
    _Entry(("редька",), ("горох", "морковь", "пастернак")),
    _Entry(
        ("огурец", "огурцы"),
        ("кукуруза", "горох", "укроп", "подсолнечник", "редис", "свекла", "фасоль", "капуста"),
    ),
    _Entry(("тыква",), ("кукуруза", "фасоль", "настурция", "мята")),
    _Entry(("кабачок", "кабачки", "цукини"), ("кукуруза", "фасоль", "укроп", "мята", "настурция")),
    _Entry(("арбуз",), ("кукуруза", "горох", "редис", "бархатцы")),
    _Entry(("дыня",), ("кукуруза", "горох", "редис", "бархатцы")),
    _Entry(
        ("морковь",),
        ("лук", "чеснок", "редис", "редька", "салат", "розмарин", "шалфей", "горох", "томат"),
    ),
    _Entry(("свекла", "свёкла"), ("лук", "фасоль кустовая", "капуста", "салат", "шпинат", "чеснок")),
    _Entry(("сельдерей",), ("капуста", "лук-порей", "томат", "фасоль", "шпинат")),
    _Entry(("пастернак",), ("горох", "лук", "редис")),
    _Entry(("хрен",), ("картофель",)),
    _Entry(("лук",), ("морковь", "свекла", "салат", "огурец", "томат", "чабер", "ромашка")),
    _Entry(("чеснок",), ("томат", "перец", "баклажан", "клубника", "морковь", "свекла", "роза")),
    _Entry(("укроп",), ("капуста", "огурец", "лук", "салат", "фенхель")),
    _Entry(("петрушка",), ("томат", "спаржа", "роза", "яблоня", "морковь")),
    _Entry(("базилик",), ("томат", "перец", "спаржа", "баклажан")),
    _Entry(("кинза", "кориандр"), ("томат", "фенхель", "шпинат", "бобы")),
    _Entry(("мята",), ("капуста", "томат", "горох")),
    _Entry(("шалфей",), ("капуста", "морковь", "розмарин", "горох")),
    _Entry(("розмарин",), ("капуста", "морковь", "фасоль")),
    _Entry(
        ("клубника",),
        ("чеснок", "лук", "шалфей", "салат", "шпинат", "бархатцы", "фасоль кустовая"),
    ),
    _Entry(("малина",), ("чеснок", "бархатцы", "пижма")),
)

EXAMPLE_CULTURES = ("томат", "огурец", "морковь", "капуста", "картофель", "клубника")


def _normalize(value: str) -> str:
    return value.strip().lower().replace("ё", "е")


def _matches(culture: str, key: str) -> bool:
    normalized_key = _normalize(key)
    return culture == normalized_key or normalized_key in culture or culture in normalized_key


def _reverse_index() -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for entry in _ENTRIES:
        culture_label = max(entry.keys, key=len)
        for neighbor in entry.neighbors:
            neighbor_key = _normalize(neighbor)
            if not neighbor_key:
                continue
            bucket = index.setdefault(neighbor_key, [])
            if culture_label not in bucket:
                bucket.append(culture_label)
    return index


_REVERSE = _reverse_index()


def find_neighbors(culture: str) -> list[str] | None:
    normalized = _normalize(culture)
    if not normalized:
        return None

    seen: set[str] = set()
    result: list[str] = []

    def append(names: list[str]) -> None:
        for name in names:
            key = _normalize(name)
            if key and key not in seen:
                seen.add(key)
                result.append(name)

    direct = _find_direct(normalized)
    if direct:
        append(direct)
    append(_find_reverse(normalized))
    return result or None


def _find_direct(normalized_culture: str) -> list[str] | None:
    for entry in _ENTRIES:
        for key in sorted(entry.keys, key=len, reverse=True):
            if _matches(normalized_culture, key):
                return list(entry.neighbors)
    return None


def _find_reverse(normalized_culture: str) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for neighbor_key, cultures in _REVERSE.items():
        if _matches(normalized_culture, neighbor_key):
            for culture in cultures:
                if culture not in seen:
                    seen.add(culture)
                    result.append(culture)
    return result
