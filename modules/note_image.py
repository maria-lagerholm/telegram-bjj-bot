import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 800
PAGE_H = 1100
ML = 70
MR = 60
MT = 80
LS = 38

INK = (30, 60, 160)
INK_LIGHT = (80, 110, 200)
LINE_CLR = (200, 210, 220)
PAPER = (255, 253, 248)
DATE_CLR = (120, 120, 130)
RED_CLR = (210, 140, 140, 80)

FONTS_DIR = Path(__file__).parent.parent / "fonts"


def _has_swedish_ext(text):
    return any(ch in text for ch in "öåäÖÅÄ")


def _has_cyrillic(text):
    return any(0x0400 <= ord(ch) <= 0x04FF for ch in text)


def load_font(size, text=""):
    p = FONTS_DIR / "Chickpeas.ttf"
    if p.exists():
        if _has_swedish_ext(text) and not _has_cyrillic(text):
            sw = FONTS_DIR / "HandwrittenThin.ttf"
            if sw.exists():
                return ImageFont.truetype(str(sw), size)
        return ImageFont.truetype(str(p), size)
    for name in ("Caveat-Regular.ttf", "CaveatBrush-Regular.ttf"):
        fp = FONTS_DIR / name
        if fp.exists():
            return ImageFont.truetype(str(fp), size)
    return ImageFont.load_default(size=size)


def _date_prefix(note):
    d = note.get("date", "")
    if not d:
        return ""
    day = note.get("day", "")
    t = note.get("time", "")
    prefix = f"{day}, {d}" if day else d
    if t:
        prefix += f" {t}"
    return prefix


def _measure_date_w(prefix, font):
    if not prefix:
        return 0
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bbox = tmp.textbbox((0, 0), prefix + "  ", font=font)
    return bbox[2] - bbox[0]


def _avg_char_w(font):
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    sample = "abcdefghijklmnopqrstuvwxyz 0123456789"
    bbox = tmp.textbbox((0, 0), sample, font=font)
    return max(1, (bbox[2] - bbox[0]) / len(sample))


def _wrap_text(text, date_w, font=None):
    usable = PAGE_W - ML - MR
    cpx = _avg_char_w(font) if font else 10
    cpl = max(20, int(usable / cpx))
    first_cpl = max(10, int((usable - date_w) / cpx))
    lines = []
    first = True
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            first = False
            continue
        if first:
            w = textwrap.wrap(para, width=first_cpl)
            if w:
                lines.append(w[0])
                left = para[len(w[0]):].strip()
                if left:
                    lines.extend(textwrap.wrap(left, width=cpl))
            first = False
        else:
            lines.extend(textwrap.wrap(para, width=cpl))
    return lines


def _note_height(note, fb, fd, ft):
    prefix = _date_prefix(note)
    dw = _measure_date_w(prefix, fd)
    lines = _wrap_text(note.get("text", ""), dw, fb)
    count = max(1, len(lines)) + 1
    if note.get("techniques"):
        count += 2
    return count * LS


def _draw_page_bg(draw, h):
    y = MT
    while y < h - 20:
        draw.line([(ML - 10, y), (PAGE_W - MR + 10, y)], fill=LINE_CLR, width=1)
        y += LS
    draw.line([(ML - 20, 0), (ML - 20, h)], fill=RED_CLR, width=2)


def _draw_note(draw, note, cy, fb, fd, ft):
    prefix = _date_prefix(note)
    dw = _measure_date_w(prefix, fd)
    lines = _wrap_text(note.get("text", ""), dw, fb)

    if prefix:
        draw.text((ML, cy), prefix + "  ", fill=DATE_CLR, font=fd)
    if lines:
        draw.text((ML + dw, cy), lines.pop(0), fill=INK, font=fb)
    cy += LS

    for line in lines:
        if not line:
            cy += LS
            continue
        draw.text((ML + (hash(line) % 3), cy), line, fill=INK, font=fb)
        cy += LS

    if note.get("techniques"):
        cy += LS
        draw.text((ML, cy), "techniques: " + ", ".join(note["techniques"]), fill=INK_LIGHT, font=ft)
        cy += LS

    return cy + LS


def render_note_image(note_text, date_str="", time_str="", day_str="", techniques=None):
    note = {"text": note_text, "date": date_str, "time": time_str, "day": day_str, "techniques": techniques}
    fb = load_font(28, text=note_text)
    fd = load_font(22, text=note_text)
    ft = load_font(20, text=note_text)

    h = max(PAGE_H, MT + _note_height(note, fb, fd, ft) + 60)
    img = Image.new("RGBA", (PAGE_W, h), PAPER + (255,))
    draw = ImageDraw.Draw(img)
    _draw_page_bg(draw, h)
    _draw_note(draw, note, MT + 4, fb, fd, ft)

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", optimize=True)
    buf.seek(0)
    buf.name = "training_note.png"
    return buf


def render_notes_page(notes_list):
    if not notes_list:
        return []

    all_text = " ".join(n.get("text", "") for n in notes_list)
    fb = load_font(28, text=all_text)
    fd = load_font(22, text=all_text)
    ft = load_font(20, text=all_text)

    max_y = PAGE_H - 60
    pages = []
    batch = []
    batch_h = MT

    for note in notes_list:
        nh = _note_height(note, fb, fd, ft)
        if batch and (batch_h + nh) > max_y:
            pages.append(batch)
            batch = [note]
            batch_h = MT + nh
        else:
            batch.append(note)
            batch_h += nh
    if batch:
        pages.append(batch)

    buffers = []
    for page_notes in pages:
        total = MT + sum(_note_height(n, fb, fd, ft) for n in page_notes) + 60
        h = max(PAGE_H, total)
        img = Image.new("RGBA", (PAGE_W, h), PAPER + (255,))
        draw = ImageDraw.Draw(img)
        _draw_page_bg(draw, h)
        cy = MT + 4
        for n in page_notes:
            cy = _draw_note(draw, n, cy, fb, fd, ft)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG", optimize=True)
        buf.seek(0)
        buf.name = "training_notes.png"
        buffers.append(buf)

    return buffers
