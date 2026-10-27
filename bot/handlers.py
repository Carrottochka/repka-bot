from __future__ import annotations

from datetime import date

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from bot.admins import claim_admin
from bot.companions import EXAMPLE_CULTURES
from bot.config import RUSTORE_URL
from bot.guide import SECTIONS, all_lessons, lesson_by_id, section_by_id
from bot.lunar import for_date
from bot.media_clips import clip_destination, clip_path
from bot.texts import (
    ABOUT,
    DOWNLOAD,
    GUIDE_INTRO,
    GUIDE_NO_CLIP,
    MENU_ABOUT,
    MENU_DOWNLOAD,
    MENU_GUIDE,
    MENU_LUNAR,
    MENU_NEIGHBORS,
    NEIGHBORS_PROMPT,
    UNKNOWN_CULTURE,
    WELCOME,
    lunar_text,
    neighbors_text,
)

router = Router()

_MENU_TEXTS = {MENU_LUNAR, MENU_NEIGHBORS, MENU_GUIDE, MENU_ABOUT, MENU_DOWNLOAD}


class NeighborForm(StatesGroup):
    waiting_name = State()


class ClipUpload(StatesGroup):
    waiting_file = State()


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_GUIDE)],
            [KeyboardButton(text=MENU_LUNAR), KeyboardButton(text=MENU_NEIGHBORS)],
            [KeyboardButton(text=MENU_ABOUT), KeyboardButton(text=MENU_DOWNLOAD)],
        ],
        resize_keyboard=True,
    )


def download_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть в RuStore", url=RUSTORE_URL)],
        ]
    )


def neighbor_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text=left.capitalize(), callback_data=f"nbr:{left}"),
            InlineKeyboardButton(text=right.capitalize(), callback_data=f"nbr:{right}"),
        ]
        for left, right in zip(EXAMPLE_CULTURES[0::2], EXAMPLE_CULTURES[1::2])
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(CommandStart())
@router.message(Command("help"))
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME, reply_markup=main_keyboard())
    await message.answer("Скачать приложение:", reply_markup=download_keyboard())


@router.message(Command("calendar"))
@router.message(F.text == MENU_LUNAR)
async def lunar(message: Message, state: FSMContext) -> None:
    await state.clear()
    today = date.today()
    await message.answer(
        lunar_text(today, for_date(today)),
        reply_markup=download_keyboard(),
    )


@router.message(Command("neighbors"))
@router.message(F.text == MENU_NEIGHBORS)
async def ask_neighbors(message: Message, state: FSMContext) -> None:
    await state.set_state(NeighborForm.waiting_name)
    await message.answer(NEIGHBORS_PROMPT, reply_markup=neighbor_keyboard())


@router.message(F.text == MENU_ABOUT)
async def about(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(ABOUT, reply_markup=download_keyboard())


@router.message(Command("guide"))
@router.message(F.text == MENU_GUIDE)
async def guide_home(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(GUIDE_INTRO, reply_markup=_sections_keyboard())


@router.message(Command("cancel"))
async def cancel_state(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_keyboard())


@router.message(Command("clip"))
async def clip_start(message: Message, state: FSMContext, command: CommandObject) -> None:
    lesson_id = (command.args or "").strip()
    found = lesson_by_id(lesson_id)
    if found is None:
        ids = "\n".join(lesson.id for lesson in all_lessons())
        await message.answer(
            "Напишите так: /clip seeds_create и следом пришлите видео.\n\n"
            f"Коды уроков:\n{ids}"
        )
        return
    user = message.from_user
    if user is None or not claim_admin(user.id):
        await message.answer("Прикладывать ролики может автор инструкции.")
        return
    await state.set_state(ClipUpload.waiting_file)
    await state.update_data(lesson_id=lesson_id)
    await message.answer(
        f"Пришлите короткий ролик для «{found[1].title}».\nОтмена — /cancel"
    )


@router.message(StateFilter(ClipUpload.waiting_file))
async def clip_receive(message: Message, state: FSMContext) -> None:
    media = message.video or message.video_note or message.animation
    if media is None and message.document is not None:
        mime = message.document.mime_type or ""
        if mime.startswith("video/"):
            media = message.document
    if media is None:
        await message.answer("Нужен видеофайл. Или отправьте /cancel.")
        return
    data = await state.get_data()
    lesson_id = str(data.get("lesson_id") or "")
    if lesson_by_id(lesson_id) is None:
        await state.clear()
        await message.answer("Урок не найден. Начните снова: /clip seeds_create")
        return
    mime = getattr(media, "mime_type", None) or ""
    if "webm" in mime:
        suffix = ".webm"
    elif "quicktime" in mime:
        suffix = ".mov"
    else:
        suffix = ".mp4"
    destination = clip_destination(lesson_id, suffix)
    await message.bot.download(media, destination=destination)
    await state.clear()
    await message.answer(
        f"Ролик для «{lesson_by_id(lesson_id)[1].title}» сохранён. "
        "Откройте этот шаг в «Инструкции» — видео придёт перед текстом.",
        reply_markup=main_keyboard(),
    )


@router.callback_query(F.data == "guide")
async def guide_sections(query: CallbackQuery) -> None:
    await query.answer()
    await _show_screen(query.message, GUIDE_INTRO, _sections_keyboard())


@router.callback_query(F.data.startswith("gs:"))
async def guide_section(query: CallbackQuery) -> None:
    section = section_by_id((query.data or "").removeprefix("gs:"))
    await query.answer()
    if section is None:
        return
    await _show_screen(query.message, section.intro, _lessons_keyboard(section.id))


@router.callback_query(F.data.startswith("gl:"))
async def guide_lesson(query: CallbackQuery) -> None:
    found = lesson_by_id((query.data or "").removeprefix("gl:"))
    await query.answer()
    if found is None:
        return
    section, lesson = found
    await _send_lesson(query.message, section.id, lesson)


@router.message(F.text == MENU_DOWNLOAD)
async def download(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(DOWNLOAD, reply_markup=download_keyboard())


@router.callback_query(F.data.startswith("nbr:"))
async def neighbor_callback(query: CallbackQuery, state: FSMContext) -> None:
    culture = (query.data or "").removeprefix("nbr:")
    await state.clear()
    await query.answer()
    await _send_neighbors(query.message, culture)


@router.message(StateFilter(NeighborForm.waiting_name), F.text)
async def neighbor_by_name(message: Message, state: FSMContext) -> None:
    culture = (message.text or "").strip()
    if not culture or culture.startswith("/") or culture in _MENU_TEXTS:
        return
    if neighbors_text(culture) is None:
        await message.answer(UNKNOWN_CULTURE, reply_markup=neighbor_keyboard())
        return
    await state.clear()
    await _send_neighbors(message, culture)


def _sections_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=section.button, callback_data=f"gs:{section.id}")]
            for section in SECTIONS
        ]
    )


def _lessons_keyboard(section_id: str) -> InlineKeyboardMarkup:
    section = section_by_id(section_id)
    rows = []
    if section is not None:
        rows.extend(
            [InlineKeyboardButton(text=lesson.button, callback_data=f"gl:{lesson.id}")]
            for lesson in section.lessons
        )
    rows.append([InlineKeyboardButton(text="К разделам", callback_data="guide")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _lesson_keyboard(section_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="К списку шагов", callback_data=f"gs:{section_id}")],
            [InlineKeyboardButton(text="Открыть в RuStore", url=RUSTORE_URL)],
        ]
    )


async def _show_screen(message: Message | None, text: str, markup: InlineKeyboardMarkup) -> None:
    if message is None or not hasattr(message, "edit_text"):
        return
    try:
        await message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest as error:
        if "message is not modified" in str(error).lower():
            return
        await message.answer(text, reply_markup=markup)


async def _send_lesson(message: Message | None, section_id: str, lesson) -> None:
    if message is None:
        return
    video = clip_path(lesson.id)
    text = lesson.body if video is not None else f"{lesson.title}\n\n{lesson.body}\n\n{GUIDE_NO_CLIP}"
    await _show_screen(message, text, _lesson_keyboard(section_id))
    if video is not None:
        await message.answer_video(FSInputFile(video), caption=lesson.title)


async def _send_neighbors(message: Message | None, culture: str) -> None:
    if message is None or not hasattr(message, "answer"):
        return
    text = neighbors_text(culture)
    if text is None:
        await message.answer(UNKNOWN_CULTURE, reply_markup=neighbor_keyboard())
        return
    await message.answer(text, reply_markup=download_keyboard())
