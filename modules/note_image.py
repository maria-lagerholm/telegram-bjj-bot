import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 900
PAGE_H = 1400
ML = 70
MR = 60
MT = 80
LS = 38

INK = (30, 60, 160)
INK_LIGHT = (80, 110, 200)
GRID_CLR = (200, 215, 225)
PAPER = (255, 253, 248)
DATE_CLR = (120, 120, 130)
HEADER_CLR = (100, 60, 30)
HEADER_LABEL = (160, 100, 60)
GRID_SZ = 28

FONTS_DIR = Path(__file__).parent.parent / "fonts"


def _has_cyrillic(text):
    return any(0x0400 <= ord(ch) <= 0x04FF for ch in text)


def load_font(size, text=""):
    if _has_cyrillic(text):
        for name in ("Chickpeas.ttf", "Caveat-Regular.ttf"):
            p = FONTS_DIR / name
            if p.exists():
                return ImageFont.truetype(str(p), size)
    for name in ("ReenieBeanie-Regular.ttf", "Caveat-Regular.ttf"):
        p = FONTS_DIR / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
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


def _note_height(note):
    text = note.get("text", "")
    prefix = _date_prefix(note)
    fd = load_font(22, text=prefix)
    fb = load_font(28, text=text)
    dw = _measure_date_w(prefix, fd)
    lines = _wrap_text(text, dw, fb)
    count = max(1, len(lines)) + 1
    if note.get("techniques"):
        count += 2
    return count * LS


def _draw_page_bg(draw, h):
    for y in range(0, h, GRID_SZ):
        draw.line([(0, y), (PAGE_W, y)], fill=GRID_CLR, width=1)
    for x in range(0, PAGE_W, GRID_SZ):
        draw.line([(x, 0), (x, h)], fill=GRID_CLR, width=1)


def _draw_note(draw, note, cy):
    text = note.get("text", "")
    prefix = _date_prefix(note)
    fd = load_font(22, text=prefix)
    fb = load_font(28, text=text)
    dw = _measure_date_w(prefix, fd)
    lines = _wrap_text(text, dw, fb)

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
        tech_text = "techniques: " + ", ".join(note["techniques"])
        ft = load_font(20, text=tech_text)
        cy += LS
        draw.text((ML, cy), tech_text, fill=INK_LIGHT, font=ft)
        cy += LS

    return cy + LS


def render_note_image(note_text, date_str="", time_str="", day_str="", techniques=None):
    note = {"text": note_text, "date": date_str, "time": time_str, "day": day_str, "techniques": techniques}

    h = max(PAGE_H, MT + _note_height(note) + 60)
    img = Image.new("RGBA", (PAGE_W, h), PAPER + (255,))
    draw = ImageDraw.Draw(img)
    _draw_page_bg(draw, h)
    _draw_note(draw, note, MT + 4)

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", optimize=True)
    buf.seek(0)
    buf.name = "training_note.png"
    return buf


def _header_height(goals, focus):
    h = 0
    if goals:
        h += LS + len(goals) * LS + LS
    if focus:
        h += LS + LS + LS
    if goals or focus:
        h += LS
    return h


def _draw_header(draw, goals, focus):
    cy = MT + 4
    if not goals and not focus:
        return cy

    label_font = load_font(22, text="goals focus")
    if goals:
        draw.text((ML, cy), "goals", fill=HEADER_LABEL, font=label_font)
        cy += LS
        for g in goals[:3]:
            marker = "o" if g.get("status") == "active" else "*"
            txt = g.get("goals", "")
            gf = load_font(28, text=txt)
            draw.text((ML + 8, cy), f"{marker} {txt}", fill=HEADER_CLR, font=gf)
            cy += LS
        cy += LS

    if focus:
        draw.text((ML, cy), "focus", fill=HEADER_LABEL, font=label_font)
        cy += LS
        txt = focus.get("technique", "")
        ff = load_font(28, text=txt)
        draw.text((ML + 8, cy), f"> {txt}", fill=HEADER_CLR, font=ff)
        cy += LS
        cy += LS

    draw.line([(ML, cy - LS // 2), (PAGE_W - MR, cy - LS // 2)], fill=HEADER_LABEL + (60,), width=1)
    return cy


def render_notes_page(notes_list, goals=None, focus=None):
    if not notes_list and not goals and not focus:
        return []

    hdr_h = _header_height(goals or [], focus)
    limit = PAGE_H - 60
    pages = []
    batch = []
    batch_h = MT + hdr_h

    for note in (notes_list or []):
        nh = _note_height(note)
        if batch and (batch_h + nh) > limit:
            pages.append(batch)
            batch = []
            batch_h = MT
        batch.append(note)
        batch_h += nh
    if batch:
        pages.append(batch)
    if not pages:
        pages.append([])

    buffers = []
    for idx, page_notes in enumerate(pages):
        extra = hdr_h if idx == 0 else 0
        total = MT + extra + sum(_note_height(n) for n in page_notes) + 60
        h = max(PAGE_H, total)
        img = Image.new("RGBA", (PAGE_W, h), PAPER + (255,))
        draw = ImageDraw.Draw(img)
        _draw_page_bg(draw, h)

        if idx == 0:
            cy = _draw_header(draw, goals or [], focus)
        else:
            cy = MT + 4

        for n in page_notes:
            cy = _draw_note(draw, n, cy)

        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG", optimize=True)
        buf.seek(0)
        buf.name = "training_notes.png"
        buffers.append(buf)

    return buffers
