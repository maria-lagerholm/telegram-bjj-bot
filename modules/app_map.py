import io

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

min_map_w = 900
box_h = 36
box_pad_x = 16
box_pad_y = 6
col_gap = 30
row_gap = 12
header_h = 70
section_gap = 24

bg = (255, 253, 248)
box_fill = (240, 245, 255)
box_stroke = (100, 130, 200)
line_col = (160, 180, 220)
text_col = (30, 40, 80)
header_col = (30, 60, 160)
sub_col = (80, 100, 160)

fonts_dir = Path(__file__).parent.parent / "fonts"

app_tree = {
    "bjj training bot": {
        "my training": [
            "write a note  /note",
            "view my notes  /notes",
            "set a goal (max 3)  /goal",
            "view my goals  /goals",
            "current focus  /focus",
            "my progress  /stats",
        ],
        "learn": [
            "technique library  /technique",
            "my toolbox  /toolbox",
        ],
        "bjj knowledge": [
            "mindset  /mindset",
            "training habits  /habits",
            "mat etiquette  /etiquette",
            "what to do  /dos",
            "what not to do  /donts",
            "competition scoring  /scoring",
            "illegal moves  /illegal",
        ],
        "settings": [
            "training schedule  /schedule",
            "reminder time  /reminders",
            "export my data  /export",
            "import backup  /import",
            "app map  /map",
            "developer link",
        ],
        "automatic reminders": [
            "daily check in (did you train?)",
            "pretraining recap (1h before)",
            "weekly goal reminder (Monday)",
            "daily focus reminder",
            "spaced repetition refreshes",
        ],
    }
}


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def load_font(size):
    font_path = fonts_dir / "CaveatBrush-Regular.ttf"
    if font_path.exists():
        return ImageFont.truetype(str(font_path), size)
    system_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/System/Library/Fonts/Noteworthy.ttc",
        "/Library/Fonts/Comic Sans MS.ttf",
    ]
    for sp in system_paths:
        if Path(sp).exists():
            return ImageFont.truetype(sp, size)
    return ImageFont.load_default(size=size)


def render_app_map():
    font_title = load_font(32)
    font_section = load_font(24)
    font_item = load_font(20)

    sections = list(app_tree["bjj training bot"].items())

    tmp_img = Image.new("RGB", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp_img)

    col_widths = []
    col_heights = []
    for sec_name, items in sections:
        w_header = text_size(tmp_draw, sec_name, font_section)[0] + box_pad_x * 2
        max_item_w = 0
        for item in items:
            iw = text_size(tmp_draw, item, font_item)[0] + box_pad_x * 2
            if iw > max_item_w:
                max_item_w = iw
        col_w = max(w_header, max_item_w, 160)
        col_widths.append(col_w)

        h = box_h + row_gap
        h += len(items) * (box_h + row_gap)
        col_heights.append(h)

    total_w = sum(col_widths) + col_gap * (len(sections) - 1) + 80
    map_w = max(min_map_w, total_w)
    max_col_h = max(col_heights)
    map_h = header_h + section_gap + max_col_h + 60

    img = Image.new("RGB", (map_w, map_h), bg)
    draw = ImageDraw.Draw(img)

    title = "bjj training bot"
    tw, th = text_size(draw, title, font_title)
    title_x = (map_w - tw) // 2
    title_y = 20
    draw.rounded_rectangle(
        [title_x - box_pad_x, title_y - box_pad_y,
         title_x + tw + box_pad_x, title_y + th + box_pad_y],
        radius=10, fill=box_fill, outline=box_stroke, width=2,
    )
    draw.text((title_x, title_y), title, fill=header_col, font=font_title)

    title_bottom = title_y + th + box_pad_y
    title_cx = map_w // 2

    col_top = header_h + section_gap
    x_cursor = (map_w - sum(col_widths) - col_gap * (len(sections) - 1)) // 2

    for i, (sec_name, items) in enumerate(sections):
        col_w = col_widths[i]
        col_cx = x_cursor + col_w // 2

        draw.line(
            [(title_cx, title_bottom), (col_cx, col_top)],
            fill=line_col, width=2,
        )

        sw, sh = text_size(draw, sec_name, font_section)
        sx = col_cx - sw // 2
        sy = col_top
        draw.rounded_rectangle(
            [sx - box_pad_x, sy - box_pad_y,
             sx + sw + box_pad_x, sy + sh + box_pad_y],
            radius=8, fill=box_fill, outline=box_stroke, width=2,
        )
        draw.text((sx, sy), sec_name, fill=sub_col, font=font_section)

        sec_bottom = sy + sh + box_pad_y

        item_y = sec_bottom + row_gap + 4
        for item_text in items:
            iw, ih = text_size(draw, item_text, font_item)
            ix = col_cx - iw // 2

            draw.line(
                [(col_cx, item_y - row_gap // 2), (col_cx, item_y)],
                fill=line_col, width=1,
            )

            draw.rounded_rectangle(
                [ix - box_pad_x, item_y - box_pad_y,
                 ix + iw + box_pad_x, item_y + ih + box_pad_y],
                radius=6, fill=(248, 250, 255), outline=(180, 195, 230), width=1,
            )
            draw.text((ix, item_y), item_text, fill=text_col, font=font_item)
            item_y += box_h + row_gap

        x_cursor += col_w + col_gap

    output = io.BytesIO()
    img.save(output, format="PNG", optimize=True)
    output.seek(0)
    output.name = "app_map.png"
    return output
