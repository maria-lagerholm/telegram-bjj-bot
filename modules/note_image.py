import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

page_w = 800
default_page_h = 1100
margin_left = 70
margin_right = 60
margin_top = 80
line_spacing = 38

ink_blue = (30, 60, 160)
ink_blue_light = (80, 110, 200)
line_grey = (200, 210, 220)
paper_white = (255, 253, 248)
date_grey = (120, 120, 130)
red_margin = (210, 140, 140, 80)

fonts_dir = Path(__file__).parent.parent / "fonts"


def load_font(size):
    font_path = fonts_dir / "CaveatBrush-Regular.ttf"
    if font_path.exists():
        return ImageFont.truetype(str(font_path), size)

    system_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/System/Library/Fonts/Noteworthy.ttc",
        "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
        "/Library/Fonts/Comic Sans MS.ttf",
    ]
    for sp in system_paths:
        if Path(sp).exists():
            return ImageFont.truetype(sp, size)

    return ImageFont.load_default(size=size)


def render_note_image(note_text, date_str="", time_str="", day_str="", techniques=None):
    font_body = load_font(28)
    font_date = load_font(22)
    font_tech = load_font(20)

    date_prefix = ""
    if date_str:
        date_prefix = date_str
        if day_str:
            date_prefix = f"{day_str}, {date_str}"
        if time_str:
            date_prefix += f" {time_str}"

    tmp = Image.new("RGB", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp)
    date_pixel_w = 0
    if date_prefix:
        date_prefix_display = date_prefix + "  "
        bbox = tmp_draw.textbbox((0, 0), date_prefix_display, font=font_date)
        date_pixel_w = bbox[2] - bbox[0]
    else:
        date_prefix_display = ""

    usable_w = page_w - margin_left - margin_right
    chars_per_line = max(30, usable_w // 14)
    first_line_chars = max(15, (usable_w - date_pixel_w) // 14)

    wrapped_lines = []
    is_first_line = True
    for paragraph in note_text.split("\n"):
        if paragraph.strip() == "":
            wrapped_lines.append("")
            is_first_line = False
            continue
        if is_first_line:
            first_wrap = textwrap.wrap(paragraph, width=first_line_chars)
            if first_wrap:
                wrapped_lines.append(first_wrap[0])
                leftover = paragraph[len(first_wrap[0]):].strip()
                if leftover:
                    wrapped_lines.extend(textwrap.wrap(leftover, width=chars_per_line))
            is_first_line = False
        else:
            wrapped_lines.extend(textwrap.wrap(paragraph, width=chars_per_line))

    tech_lines = 2 if techniques else 0
    total_lines = len(wrapped_lines) + tech_lines + 2
    needed_h = margin_top + total_lines * line_spacing + 60
    img_h = max(default_page_h, needed_h)

    img = Image.new("RGBA", (page_w, img_h), paper_white + (255,))
    draw = ImageDraw.Draw(img)

    y = margin_top
    while y < img_h - 20:
        draw.line(
            [(margin_left - 10, y), (page_w - margin_right + 10, y)],
            fill=line_grey,
            width=1,
        )
        y += line_spacing

    draw.line(
        [(margin_left - 20, 0), (margin_left - 20, img_h)],
        fill=red_margin,
        width=2,
    )

    cursor_y = margin_top + 4
    if date_prefix:
        draw.text((margin_left, cursor_y), date_prefix_display, fill=date_grey, font=font_date)

    if wrapped_lines:
        first_line = wrapped_lines.pop(0)
        x_after_date = margin_left + date_pixel_w
        draw.text((x_after_date, cursor_y), first_line, fill=ink_blue, font=font_body)
    cursor_y += line_spacing

    for line in wrapped_lines:
        if line == "":
            cursor_y += line_spacing
            continue
        x_offset = margin_left + (hash(line) % 3)
        draw.text((x_offset, cursor_y), line, fill=ink_blue, font=font_body)
        cursor_y += line_spacing

    if techniques:
        cursor_y += line_spacing
        tech_text = "techniques: " + ", ".join(techniques)
        draw.text((margin_left, cursor_y), tech_text, fill=ink_blue_light, font=font_tech)

    output = io.BytesIO()
    img = img.convert("RGB")
    img.save(output, format="PNG", optimize=True)
    output.seek(0)
    output.name = "training_note.png"
    return output
