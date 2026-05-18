#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word (.docx) generation for Lozenets Lounge offer documents.
Mirrors the content of pdf_builder.py using python-docx.
"""

import os
from io import BytesIO

from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Brand colours ──────────────────────────────────────────────────────────
GREEN = RGBColor(0x19, 0x51, 0x4A)
GOLD  = RGBColor(0xE9, 0xD2, 0x81)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREY  = RGBColor(0xCC, 0xCC, 0xCC)
TINT  = RGBColor(0xEA, 0xF1, 0xF0)
TOTAL_BG = RGBColor(0xD4, 0xEA, 0xE7)

_DIR      = os.path.dirname(os.path.abspath(__file__))
LOGO_ICON = os.path.join(_DIR, "logo_icon.png")


# ── Low-level XML helpers ──────────────────────────────────────────────────
def _set_cell_bg(cell, rgb: RGBColor):
    """Fill a table cell background with a solid colour."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    hex_color = f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)


def _set_cell_border(cell, **edges):
    """Add borders to a cell. edges keys: top, bottom, left, right."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge, (color, sz) in edges.items():
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"),   "single")
        el.set(qn("w:sz"),    str(sz))
        el.set(qn("w:color"), color)
        borders.append(el)
    tcPr.append(borders)


def _run(para, text, bold=False, italic=False,
         color: RGBColor = None, size: int = 10):
    run = para.add_run(text)
    run.bold   = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = "Calibri"
    if color:
        run.font.color.rgb = color
    return run


def _heading(doc: Document, text: str):
    """Section heading — green bold with gold bottom border."""
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(14)
    para.paragraph_format.space_after  = Pt(4)
    run = para.add_run(text)
    run.bold = True
    run.font.size = Pt(12)
    run.font.name = "Calibri"
    run.font.color.rgb = GREEN
    # Gold bottom border via paragraph XML
    pPr  = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bot  = OxmlElement("w:bottom")
    bot.set(qn("w:val"),   "single")
    bot.set(qn("w:sz"),    "6")
    bot.set(qn("w:color"), "E9D281")
    pBdr.append(bot)
    pPr.append(pBdr)
    return para


def _body(doc: Document, text: str, bold=False, space_after: int = 3):
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(space_after)
    _run(para, text, bold=bold)
    return para


# ══════════════════════════════════════════════════════════════════════════
#  MAIN BUILDER
# ══════════════════════════════════════════════════════════════════════════
def build_word(data: dict, output):
    """
    Build the offer as a .docx file.
    `output` — file path (str) or BytesIO object.
    `data`   — same dict as build_pdf() expects.
    """
    doc = Document()

    # ── Page margins ───────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

        # Header
        hdr  = section.header
        hdr.is_linked_to_previous = False
        hp   = hdr.paragraphs[0]
        hp.clear()
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if os.path.exists(LOGO_ICON):
            try:
                run = hp.add_run()
                run.add_picture(LOGO_ICON, height=Cm(1.8))
            except Exception:
                _run(hp, "Lozenets Lounge", bold=True, size=14, color=GREEN)
        else:
            _run(hp, "Lozenets Lounge", bold=True, size=14, color=GREEN)

        # Footer
        ftr = section.footer
        ftr.is_linked_to_previous = False
        fp  = ftr.paragraphs[0]
        fp.clear()
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _run(fp,
             "Instagram: @lozenets_lounge  |  Facebook: Lozenets Lounge  |  "
             "lozenetslounge.eu  |  София, Лозенец, ул. Кръстьо Сарафов 22",
             size=8, color=GREEN)

    # ── Greeting ───────────────────────────────────────────────────────────
    client = (data.get("client_name") or "").strip() or "___________________"
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    _run(p, "Уважаеми/а ")
    _run(p, client, bold=True)
    _run(p, ",")

    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(10)
    _run(p2, "Благодарим Ви за интереса към Lozenets Lounge. "
             "Представяме Ви следната оферта за Вашето събитие:")

    # ── 2. Event description ───────────────────────────────────────────────
    _heading(doc, "2. Описание на събитие")
    desc = (data.get("event_description") or "").strip()
    for line in (desc.splitlines() if desc else ["…"]):
        if line.strip():
            _body(doc, line.strip())

    # ── 2.1 What's included ────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(4)
    _run(p, "2.1. Какво е включено:", bold=True, color=GREEN)

    items = [i.strip() for i in data.get("included_items", []) if i.strip()]
    for item in (items or ["…"]):
        _body(doc, f"●  {item}")

    # ── 3. Pricing ─────────────────────────────────────────────────────────
    _heading(doc, "3. Цена")

    price_rows = data.get("price_rows", [])
    col_count  = 5
    tbl = doc.add_table(rows=1, cols=col_count)
    tbl.style = "Table Grid"
    tbl.autofit = False

    # Column widths (cm)
    widths = [5.5, 2.8, 3.0, 2.8, 2.5]
    for i, w in enumerate(widths):
        tbl.columns[i].width = Cm(w)

    # Header row
    hdr_row = tbl.rows[0]
    hdr_labels = ["Описание", "Цена / час", "Продължителност", "Отстъпка", "Общо"]
    for i, (cell, label) in enumerate(zip(hdr_row.cells, hdr_labels)):
        _set_cell_bg(cell, GREEN)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _run(p, label, bold=True, color=WHITE, size=9)

    # Data rows
    for ri, row in enumerate(price_rows):
        tr = tbl.add_row()
        vals = [
            row.get("description",    ""),
            row.get("price_per_hour", ""),
            row.get("duration",       ""),
            row.get("fees",           ""),
            row.get("total",          ""),
        ]
        bg = TINT if ri % 2 == 1 else None
        for i, (cell, val) in enumerate(zip(tr.cells, vals)):
            if bg:
                _set_cell_bg(cell, bg)
            p = cell.paragraphs[0]
            if i == col_count - 1:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            _run(p, str(val or ""), size=10)

    # Total row
    tot_row = tbl.add_row()
    _set_cell_bg(tot_row.cells[0], TOTAL_BG)
    # Merge first 4 cells for label
    merged = tot_row.cells[0].merge(tot_row.cells[1])
    merged = merged.merge(tot_row.cells[1])
    merged = merged.merge(tot_row.cells[1])
    lp = tot_row.cells[0].paragraphs[0]
    _run(lp, "Обща цена (вкл. ДДС)", bold=True, size=10)
    _set_cell_bg(tot_row.cells[-1], TOTAL_BG)
    vp = tot_row.cells[-1].paragraphs[0]
    vp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _run(vp, data.get("total_vat_str", "—"), bold=True, size=10)

    doc.add_paragraph()  # spacer

    # ── 4. Additional services ─────────────────────────────────────────────
    _heading(doc, "4. Допълнителни Услуги")
    service_defs = [
        ("bar",        "Бар и пакет с напитки",       "цена при запитване"),
        ("catering",   "Кетъринг / бюфет",            "цена при запитване"),
        ("flowers",    "Флорална декорация",           "цена при запитване"),
        ("photo",      "Фотография / видеозаснемане",  "цена и наличност при запитване"),
        ("extra_time", "Удължено време за подготовка", "€50 / час"),
    ]
    services  = data.get("additional_services", {})
    any_shown = False
    for key, label, price in service_defs:
        svc = services.get(key, {})
        if svc.get("selected"):
            any_shown = True
            note = (svc.get("note") or "").strip()
            note_part = f" — {note}" if note else ""
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(3)
            _run(p, "✓  ", bold=True, color=GREEN)
            _run(p, label, bold=True)
            _run(p, f"  ({price}){note_part}", color=RGBColor(0x88, 0x88, 0x88))
    if not any_shown:
        _body(doc, "Не са избрани допълнителни услуги.")

    # ── 5. Terms & Conditions ──────────────────────────────────────────────
    _heading(doc, "5. Условия")
    terms = [
        "За потвърждаване на резервацията се изисква 30% депозит. "
        "Оставащата сума се заплаща 3 дни преди събитието.",
        "При анулация, направена повече от 10 дни преди събитието, депозитът се "
        "възстановява изцяло. При анулация в рамките на 10 дни преди събитието "
        "депозитът не подлежи на възстановяване.",
        "Всякакви щети по обекта или оборудването, причинени по време на събитието, "
        "са отговорност на клиента.",
        "След 22:00 ч. се прилагат ограничения за шума. Lozenets Lounge си запазва "
        "правото да следи за спазването им.",
        "Внасянето на външни храни и напитки подлежи на предварителна уговорка.",
        "Плащанията се извършват по банков път.",
    ]
    for i, term in enumerate(terms, 1):
        _body(doc, f"{i}.  {term}")

    # ── 6. Validity ────────────────────────────────────────────────────────
    _heading(doc, "6. Валидност")
    valid_until = (data.get("valid_until") or "").strip() or "_____________________________"
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(16)
    _run(p, "Офертата е валидна до: ")
    _run(p, valid_until, bold=True)
    _run(p, ".")

    # ── 7. Signatures ──────────────────────────────────────────────────────
    _heading(doc, "7. Съгласие и подписи")
    sig_tbl = doc.add_table(rows=2, cols=2)
    sig_tbl.autofit = False
    for col in sig_tbl.columns:
        col.width = Cm(9)
    labels = ["Даниела Боянова-Колева (Подпис и Дата)", "Клиент (Подпис и Дата)"]
    lines  = ["____________________________",           "____________________________"]
    for i, cell in enumerate(sig_tbl.rows[0].cells):
        _run(cell.paragraphs[0], labels[i], size=9)
    for i, cell in enumerate(sig_tbl.rows[1].cells):
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(20)
        _run(p, lines[i], size=9)

    doc.save(output)
