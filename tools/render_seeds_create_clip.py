"""Схема шага «Создать семена» в цветах РЕПКИ. Не запись экрана телефона."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
CAPTION = 96
NAV = 104
BG = (237, 237, 237)
GREEN = (127, 187, 63)
GREEN_DARK = (57, 77, 18)
INK = (45, 12, 53)
MUTED = (95, 78, 99)
LINE = (224, 224, 224)
WHITE = (255, 255, 255)
SHADOW = (210, 210, 210)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "guide" / "seeds_create.mp4"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    path = Path(r"C:\Windows\Fonts") / name
    if not path.is_file():
        path = Path(r"C:\Windows\Fonts\arial.ttf")
    return ImageFont.truetype(str(path), size)


FONT = font(22)
FONT_SM = font(16)
FONT_MD = font(20)
FONT_B = font(28, bold=True)
FONT_CAPTION = font(26, bold=True)
FONT_CHIP = font(18)


def new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (W, H), BG)
    return image, ImageDraw.Draw(image)


def toolbar(draw: ImageDraw.ImageDraw, title: str) -> None:
    draw.rectangle((0, 0, W, 100), fill=BG)
    draw.line((36, 50, 58, 50), fill=INK, width=4)
    draw.line((36, 50, 48, 38), fill=INK, width=4)
    draw.line((36, 50, 48, 62), fill=INK, width=4)
    draw.text((76, 50), title, font=FONT_B, fill=INK, anchor="lm")


def bottom_nav(draw: ImageDraw.ImageDraw, active: str = "Семена") -> None:
    top = H - CAPTION - NAV
    draw.rectangle((0, top, W, top + NAV), fill=WHITE)
    draw.line((0, top, W, top), fill=LINE, width=2)
    items = ("Главная", "Семена", "Многол.", "Участок", "Календ.", "Журнал", "Заметки")
    for index, name in enumerate(items):
        cx = int((index + 0.5) * W / len(items))
        selected = name == active
        if selected:
            draw.rounded_rectangle((cx - 40, top + 14, cx + 40, top + 58), 18, fill=GREEN)
        color = WHITE if selected else MUTED
        draw.ellipse((cx - 12, top + 24, cx + 12, top + 48), outline=color, width=3)
        draw.text((cx, top + 78), name, font=font(15), fill=GREEN_DARK if selected else MUTED, anchor="mm")


def caption(draw: ImageDraw.ImageDraw, text: str) -> None:
    top = H - CAPTION
    draw.rectangle((0, top, W, H), fill=GREEN_DARK)
    draw.text((32, top + CAPTION / 2), text, font=FONT_CAPTION, fill=WHITE, anchor="lm")


def fab(draw: ImageDraw.ImageDraw, hot: bool = False) -> None:
    cx, cy, radius = 620, H - CAPTION - NAV - 78, 42
    if hot:
        draw.ellipse((cx - 64, cy - 64, cx + 64, cy + 64), outline=GREEN, width=7)
    draw.ellipse((cx - radius + 3, cy - radius + 5, cx + radius + 3, cy + radius + 5), fill=SHADOW)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=GREEN)
    draw.line((cx - 16, cy, cx + 16, cy), fill=WHITE, width=6)
    draw.line((cx, cy - 16, cx, cy + 16), fill=WHITE, width=6)


def search_bar(draw: ImageDraw.ImageDraw, y: int) -> None:
    draw.rounded_rectangle((24, y, W - 24, y + 68), 16, fill=WHITE, outline=LINE, width=2)
    draw.text((48, y + 34), "Поиск семян...", font=FONT, fill=MUTED, anchor="lm")


def chips(draw: ImageDraw.ImageDraw, y: int) -> None:
    x = 24
    for label in ("Посажено", "Лучшие", "Сидераты"):
        width = int(FONT_CHIP.getlength(label)) + 40
        draw.rounded_rectangle((x, y, x + width, y + 50), 25, fill=WHITE, outline=LINE, width=2)
        draw.text((x + width / 2, y + 25), label, font=FONT_CHIP, fill=INK, anchor="mm")
        x += width + 12


def seed_card(draw: ImageDraw.ImageDraw, y: int) -> None:
    draw.rounded_rectangle((24, y, W - 24, y + 128), 18, fill=WHITE, outline=LINE, width=2)
    draw.rectangle((24, y + 16, 34, y + 112), fill=GREEN)
    draw.text((56, y + 42), "Томат", font=FONT_B, fill=INK, anchor="lm")
    draw.text((56, y + 86), "Бычье сердце  ·  в наличии", font=FONT_MD, fill=MUTED, anchor="lm")


def field(draw: ImageDraw.ImageDraw, y: int, label: str, value: str | None = None, hot: bool = False) -> None:
    outline = GREEN if hot else LINE
    draw.rounded_rectangle((24, y, W - 24, y + 82), 14, fill=WHITE, outline=outline, width=4 if hot else 2)
    if value:
        draw.text((44, y + 24), label, font=FONT_SM, fill=MUTED, anchor="lm")
        draw.text((44, y + 54), value, font=FONT, fill=INK, anchor="lm")
    else:
        draw.text((44, y + 41), label, font=FONT, fill=MUTED, anchor="lm")


def finish(draw: ImageDraw.ImageDraw, text: str) -> None:
    bottom_nav(draw)
    caption(draw, text)


def scene_open() -> Image.Image:
    image, draw = new_canvas()
    toolbar(draw, "РЕПКА")
    draw.text((48, 280), "Учёт семян и участка", font=FONT_B, fill=INK, anchor="lm")
    draw.text((48, 340), "Инструкция внизу экрана", font=FONT, fill=MUTED, anchor="lm")
    finish(draw, "1. Откройте «Семена»")
    return image


def scene_list(hot_fab: bool, text: str) -> Image.Image:
    image, draw = new_canvas()
    toolbar(draw, "В наличии")
    search_bar(draw, 124)
    chips(draw, 212)
    draw.text((48, 340), "Семена не найдены", font=FONT, fill=MUTED, anchor="lm")
    draw.text((48, 390), "Нажмите «+», чтобы добавить", font=FONT_MD, fill=MUTED, anchor="lm")
    fab(draw, hot=hot_fab)
    finish(draw, text)
    return image


def scene_form_main(filled: bool) -> Image.Image:
    image, draw = new_canvas()
    toolbar(draw, "Добавить семена")
    draw.text((32, 124), "Основная информация", font=font(22, bold=True), fill=INK, anchor="lm")
    if filled:
        field(draw, 160, "Культура", "Томат")
        field(draw, 258, "Сорт", "Бычье сердце")
        field(draw, 356, "Количество, шт", "20")
        field(draw, 454, "Производитель", "Гавриш")
        caption_text = "3. Количество и производитель"
    else:
        field(draw, 160, "Культура", hot=True)
        field(draw, 258, "Сорт", hot=True)
        field(draw, 356, "Количество, шт")
        field(draw, 454, "Производитель")
        caption_text = "2. Культура и сорт"
    finish(draw, caption_text)
    return image


def scene_planting() -> Image.Image:
    image, draw = new_canvas()
    toolbar(draw, "Добавить семена")
    draw.text((32, 140), "Тип посадки", font=font(22, bold=True), fill=INK, anchor="lm")
    draw.rounded_rectangle((24, 190, 348, 274), 16, fill=GREEN)
    draw.text((186, 232), "Рассада", font=FONT_B, fill=WHITE, anchor="mm")
    draw.rounded_rectangle((364, 190, W - 24, 274), 16, fill=WHITE, outline=LINE, width=2)
    draw.text((530, 232), "Грунт", font=FONT_B, fill=INK, anchor="mm")
    draw.text((32, 320), "Активная кнопка зелёная.", font=FONT, fill=MUTED, anchor="lm")
    draw.text((32, 368), "Сначала выбрана «Рассада».", font=FONT, fill=MUTED, anchor="lm")
    finish(draw, "4. Выберите тип посадки")
    return image


def scene_dates() -> Image.Image:
    image, draw = new_canvas()
    toolbar(draw, "Добавить семена")
    field(draw, 130, "Дата посадки", "01.04.2026")
    field(draw, 228, "Срок годности", "01.04.2028")
    field(draw, 326, "Глубина заделки (см)", "1")
    field(draw, 424, "Между растениями (см)", "40")
    field(draw, 522, "Между рядами (см)", "60")
    field(draw, 620, "Срок созревания (дней)", "110")
    finish(draw, "5. Даты, глубина, расстояния")
    return image


def scene_save() -> Image.Image:
    image, draw = new_canvas()
    toolbar(draw, "Добавить семена")
    field(draw, 140, "Культура", "Томат")
    field(draw, 238, "Сорт", "Бычье сердце")
    draw.rounded_rectangle((24, 380, W - 24, 468), 18, fill=GREEN)
    draw.text((W / 2, 424), "Сохранить", font=FONT_B, fill=WHITE, anchor="mm")
    draw.rounded_rectangle((16, 368, W - 16, 480), 22, outline=GREEN_DARK, width=4)
    finish(draw, "6. Нажмите «Сохранить»")
    return image


def scene_photo() -> Image.Image:
    image, draw = new_canvas()
    toolbar(draw, "Добавить семена")
    field(draw, 140, "Культура", "Томат")
    overlay = Image.new("RGBA", (W, H), (45, 12, 53, 90))
    image.paste(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((48, 420, W - 48, 820), 24, fill=WHITE)
    draw.text((80, 480), "Фото упаковки", font=FONT_B, fill=INK, anchor="lm")
    draw.text((80, 550), "Лицевая сторона и оборот.", font=FONT, fill=MUTED, anchor="lm")
    draw.text((80, 600), "Только 2 фото. Можно пропустить.", font=FONT, fill=MUTED, anchor="lm")
    draw.rounded_rectangle((80, 680, W - 80, 756), 16, fill=GREEN)
    draw.text((W / 2, 718), "Сделать фото", font=FONT_B, fill=WHITE, anchor="mm")
    bottom_nav(draw)
    caption(draw, "7. Фото можно пропустить")
    return image


def scene_done() -> Image.Image:
    image, draw = new_canvas()
    toolbar(draw, "В наличии")
    search_bar(draw, 124)
    chips(draw, 212)
    seed_card(draw, 290)
    fab(draw, hot=False)
    finish(draw, "Карточка сохранена")
    return image


def build_frames() -> list[Image.Image]:
    frames: list[Image.Image] = []

    def hold(image: Image.Image, count: int) -> None:
        frames.extend([image] * count)

    hold(scene_open(), 10)
    hold(scene_list(False, "Зелёный «+» справа внизу"), 8)
    hold(scene_list(True, "Нажмите «+»"), 10)
    hold(scene_form_main(False), 12)
    hold(scene_form_main(True), 12)
    hold(scene_planting(), 12)
    hold(scene_dates(), 14)
    hold(scene_save(), 10)
    hold(scene_photo(), 12)
    hold(scene_done(), 14)
    return frames


def encode(frames: list[Image.Image], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        folder_path = Path(folder)
        for index, frame in enumerate(frames):
            frame.save(folder_path / f"frame_{index:04d}.png")
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.check_call(
            [
                ffmpeg,
                "-y",
                "-framerate",
                "8",
                "-i",
                str(folder_path / "frame_%04d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                "-crf",
                "28",
                "-an",
                str(destination),
            ]
        )


def main() -> None:
    encode(build_frames(), OUT)
    print(f"{OUT} {OUT.stat().st_size}")


if __name__ == "__main__":
    main()
