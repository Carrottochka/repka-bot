"""Приближённый лунный календарь садовода.

Повторяет расчёт из app/.../domain/util/LunarGardenCalendar.kt,
чтобы подсказка в боте совпадала с подсказкой в приложении.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

_ZODIAC_RU = (
    "Овен",
    "Телец",
    "Близнецы",
    "Рак",
    "Лев",
    "Дева",
    "Весы",
    "Скорпион",
    "Стрелец",
    "Козерог",
    "Водолей",
    "Рыбы",
)

_SIGN_HINTS = (
    "Быстрый рост — салаты, редис",
    "Корни и плоды, устойчивость",
    "Листья, черенкование",
    "Полив, влаголюбивые",
    "Плоды, формирование",
    "Прополка, порядок",
    "Цветы, декоративные",
    "Питание, корневая зона",
    "Сбор, семена, сушка",
    "Структура почвы, корни",
    "Лёгкие культуры",
    "Компост, мульча, органика",
)

_SIGN_GARDEN = (
    "Луна в Овне: быстрые культуры, уход за молодыми всходами.",
    "Луна в Тельце: лук, корнеплоды, подкормка под корень.",
    "Луна в Близнецах: зелень, прореживание, пасынкование.",
    "Луна в Раке: полив, влаголюбивые, накопление силы растений.",
    "Луна во Льве: плоды, борьба с вредителями, подкормка плодоносящих.",
    "Луна в Деве: прополка, санитарная обрезка, чистота грядок.",
    "Луна в Весах: цветы, декоративные, формирование кроны.",
    "Луна в Скорпионе: корни, влагопитание, внекорневые подкормки.",
    "Луна в Стрельце: сбор, сушка трав, заготовка семян.",
    "Луна в Козероге: длительные культуры, укрепление корней.",
    "Луна в Водолее: аэрация, парники, лёгкие работы.",
    "Луна в Рыбах: компост, мульча, органические подкормки.",
)


@dataclass(frozen=True)
class LunarInfo:
    phase_title: str
    phase_description: str
    illumination_percent: int
    is_waxing: bool
    zodiac_sign: str
    sign_hint: str
    primary_advice: str
    secondary_advice: str


def for_date(day: date) -> LunarInfo:
    jd = _gregorian_to_julian_day(day.year, day.month, day.day)
    synodic = 29.530588853
    ref_new_moon = 2451550.09765
    age = ((jd - ref_new_moon) % synodic + synodic) % synodic
    phase_fraction = age / synodic
    illumination = (1.0 - math.cos(2 * math.pi * phase_fraction)) / 2.0 * 100.0
    illumination_percent = max(0, min(100, round(illumination)))
    is_waxing = phase_fraction < 0.5

    t = (jd - 2451545.0) / 36525.0
    moon_lon = (218.316 + 481267.881 * t) % 360.0
    if moon_lon < 0:
        moon_lon += 360.0
    sign_idx = max(0, min(11, int(moon_lon / 30.0)))
    primary, secondary = _build_advice(phase_fraction, sign_idx)
    trend = "Растущая луна" if is_waxing else "Убывающая луна"
    return LunarInfo(
        phase_title=_phase_name_ru(phase_fraction),
        phase_description=f"Возраст цикла: {age:.1f} сут. {trend}.",
        illumination_percent=illumination_percent,
        is_waxing=is_waxing,
        zodiac_sign=_ZODIAC_RU[sign_idx],
        sign_hint=_SIGN_HINTS[sign_idx],
        primary_advice=primary,
        secondary_advice=secondary,
    )


def _phase_name_ru(phase_fraction: float) -> str:
    phase = phase_fraction * 8.0
    if phase < 1.0:
        return "Новолуние"
    if phase < 2.0:
        return "Растущий серп"
    if phase < 3.0:
        return "Первая четверть"
    if phase < 4.0:
        return "Растущая Луна"
    if phase < 5.0:
        return "Полнолуние"
    if phase < 6.0:
        return "Убывающая Луна"
    if phase < 7.0:
        return "Последняя четверть"
    return "Убывающий серп"


def _build_advice(phase_fraction: float, sign_idx: int) -> tuple[str, str]:
    if phase_fraction < 0.05 or phase_fraction > 0.95:
        phase_advice = (
            "Новолуние: удобно планировать работы и готовить грунт; "
            "посев по луне — после стабилизации фазы."
        )
    elif 0.45 < phase_fraction < 0.55:
        phase_advice = (
            "Полнолуние: сильный сокодвиж — хорошо для сбора урожая и заготовок; "
            "посадку корней лучше отложить."
        )
    elif phase_fraction < 0.5:
        phase_advice = (
            "Растущая луна: ориентир на наземные культуры, зелень, пасынкование и прививки."
        )
    else:
        phase_advice = (
            "Убывающая луна: ориентир на корни, луковицы, обрезку и пересадку с корневой зоной."
        )
    return phase_advice, _SIGN_GARDEN[sign_idx]


def _gregorian_to_julian_day(year: int, month: int, day: int) -> float:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn + 0.5
