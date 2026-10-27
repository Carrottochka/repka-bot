from __future__ import annotations

from datetime import date

from bot.companions import find_neighbors
from bot.config import DEVELOPER_EMAIL, RUSTORE_URL
from bot.lunar import LunarInfo

MENU_LUNAR = "Лунный день"
MENU_NEIGHBORS = "Соседи на грядке"
MENU_GUIDE = "Инструкция"
MENU_ABOUT = "Что умеет Репка"
MENU_DOWNLOAD = "Скачать"

_MONTHS = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)


def format_day(day: date) -> str:
    return f"{day.day} {_MONTHS[day.month - 1]} {day.year}"


WELCOME = (
    "РЕПКА — учёт семян, грядок, многолетников и работ в саду.\n\n"
    "«Инструкция» разбирает экраны приложения по шагам. "
    "«Лунный день» и «Соседи на грядке» — короткие подсказки. "
    "Журнал участка ведётся в самом приложении."
)

GUIDE_INTRO = (
    "Инструкция по РЕПКЕ.\n"
    "Выберите раздел. Если к шагу уже записан короткий ролик, он придёт перед текстом."
)

GUIDE_NO_CLIP = "Короткий ролик к этому шагу ещё не записан."

ABOUT = (
    "В приложении РЕПКА можно:\n"
    "• вести семена и свои сборы\n"
    "• рисовать участок и сажать культуры по ячейкам\n"
    "• хранить деревья, кусты и уход за ними\n"
    "• записывать наблюдения и заметки\n"
    "• ставить задачи в календарь работ\n"
    "• смотреть лунный день и советы по культурам\n\n"
    "Фото сверх бесплатного лимита и расписания ухода — в Репка Premium. "
    "Остальное доступно без подписки."
)

NEIGHBORS_PROMPT = (
    "Напишите культуру — например, томат, морковь или клубника.\n"
    "Или выберите одну из кнопок ниже."
)

DOWNLOAD = (
    "РЕПКА в RuStore:\n"
    f"{RUSTORE_URL}\n\n"
    f"Вопросы и идеи: {DEVELOPER_EMAIL}"
)

UNKNOWN_CULTURE = (
    "В справочнике нет такой культуры.\n"
    "Попробуйте томат, огурец, морковь, капуста, картофель или клубника."
)


def lunar_text(day: date, info: LunarInfo) -> str:
    return (
        f"Лунный календарь на {format_day(day)}\n\n"
        f"{info.phase_title} · освещённость ~{info.illumination_percent}%\n"
        f"Луна в знаке {info.zodiac_sign}: {info.sign_hint}\n\n"
        f"{info.primary_advice}\n"
        f"{info.secondary_advice}\n\n"
        "Это ориентир для работ, не астрономический прогноз. "
        "В Репке тот же день открывается в календаре вместе с вашими задачами."
    )


def neighbors_text(culture: str) -> str | None:
    neighbors = find_neighbors(culture)
    if not neighbors:
        return None
    title = culture.strip()
    listed = ", ".join(neighbors)
    return (
        f"Соседи для «{title}»\n\n"
        f"{listed}\n\n"
        "В карточке семян Репки этот список уже есть, и к нему можно добавить своих соседей."
    )
