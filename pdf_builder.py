#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF generation for Lozenets Lounge offer documents.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Font registration ──────────────────────────────────────────────────────
_FONT_CANDIDATES = [
    (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
    ),
    (
        "/System/Library/Fonts/Supplemental/Tahoma.ttf",
        "/System/Library/Fonts/Supplemental/Tahoma Bold.ttf",
        None, None,
    ),
]

REG = BOLD = ITALIC = BOLD_ITALIC = None
for _r, _b, _i, _bi in _FONT_CANDIDATES:
    if os.path.exists(_r) and os.path.exists(_b):
        pdfmetrics.registerFont(TTFont("OfferReg",  _r))
        pdfmetrics.registerFont(TTFont("OfferBold", _b))
        if _i  and os.path.exists(_i):  pdfmetrics.registerFont(TTFont("OfferItalic",     _i))
        if _bi and os.path.exists(_bi): pdfmetrics.registerFont(TTFont("OfferBoldItalic", _bi))
        REG        = "OfferReg"
        BOLD       = "OfferBold"
        ITALIC     = "OfferItalic"     if (_i  and os.path.exists(_i))  else "OfferReg"
        BOLD_ITALIC= "OfferBoldItalic" if (_bi and os.path.exists(_bi)) else "OfferBold"
        break

if not REG:
    raise RuntimeError("No Cyrillic-capable font found (Arial or Tahoma required).")

# ── Brand colours ──────────────────────────────────────────────────────────
BRAND_GREEN = colors.HexColor("#19514A")
BRAND_GOLD  = colors.HexColor("#E9D281")
BRAND_CREAM = colors.HexColor("#F5F0E8")
ROW_TINT    = colors.HexColor("#EAF1F0")
MID_GREY    = colors.HexColor("#CCCCCC")
WHITE       = colors.white

PAGE_W, PAGE_H = A4
MARGIN   = 2.0 * cm
HEADER_H = 3.4 * cm
FOOTER_H = 2.6 * cm   # taller to accommodate logo in footer

_HERE      = os.path.dirname(os.path.abspath(__file__))
LOGO_HOUSE = os.path.join(_HERE, "logo_house.png")
LOGO_ICON  = os.path.join(_HERE, "logo_icon.png")


# ── Page header + footer ───────────────────────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # ═══ HEADER ════════════════════════════════════════════════════════════
    canvas.setFillColor(BRAND_GREEN)
    canvas.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)

    # Gold accent line beneath header
    canvas.setFillColor(BRAND_GOLD)
    canvas.rect(0, h - HEADER_H - 0.10 * cm, w, 0.10 * cm, fill=1, stroke=0)

    # Logo image centred in header — no additional text
    logo_path = LOGO_ICON if os.path.exists(LOGO_ICON) else (
                LOGO_HOUSE if os.path.exists(LOGO_HOUSE) else None)
    if logo_path:
        logo_h = HEADER_H * 0.82
        logo_w = logo_h
        logo_x = (w - logo_w) / 2          # horizontally centred
        logo_y = h - HEADER_H + (HEADER_H - logo_h) / 2
        try:
            canvas.drawImage(
                logo_path, logo_x, logo_y,
                width=logo_w, height=logo_h,
                mask="auto", preserveAspectRatio=True,
            )
        except Exception:
            pass

    # ═══ FOOTER ════════════════════════════════════════════════════════════
    canvas.setFillColor(BRAND_GREEN)
    canvas.rect(0, 0, w, FOOTER_H, fill=1, stroke=0)

    # Gold accent line above footer
    canvas.setFillColor(BRAND_GOLD)
    canvas.rect(0, FOOTER_H, w, 0.09 * cm, fill=1, stroke=0)

    # Logo in footer (right side, full height)
    if logo_path:
        foot_logo_h = FOOTER_H * 0.82
        foot_logo_w = foot_logo_h
        foot_logo_y = (FOOTER_H - foot_logo_h) / 2
        try:
            canvas.drawImage(
                logo_path,
                w - MARGIN - foot_logo_w, foot_logo_y,
                width=foot_logo_w, height=foot_logo_h,
                mask="auto", preserveAspectRatio=True,
            )
        except Exception:
            pass

    # Contact text (left side of footer)
    canvas.setFont(REG, 7.5)
    canvas.setFillColor(WHITE)
    canvas.drawString(MARGIN, FOOTER_H * 0.65,
                      "Instagram: @lozenets_lounge   |   Facebook: Lozenets Lounge")
    canvas.drawString(MARGIN, FOOTER_H * 0.33,
                      "Website: lozenetslounge.eu   |   София, Лозенец, ул. Кръстьо Сарафов 22")

    canvas.restoreState()


# ── Main builder ───────────────────────────────────────────────────────────
def build_pdf(data: dict, output):
    """
    Build the offer PDF.
    `output` can be a file path (str) or a BytesIO object.
    """
    doc = BaseDocTemplate(
        output,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HEADER_H + 0.6 * cm,
        bottomMargin=FOOTER_H + 0.4 * cm,
    )

    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        PAGE_W - 2 * MARGIN,
        PAGE_H - HEADER_H - FOOTER_H - 1.0 * cm,
        id="main",
    )
    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=_header_footer)
    ])

    # ── Styles ─────────────────────────────────────────────────────────────
    def S(name, **kw):
        base = dict(fontName=REG, fontSize=10, leading=14, spaceAfter=3)
        base.update(kw)
        return ParagraphStyle(name, **base)

    s_body    = S("body")
    s_bold    = S("bold",    fontName=BOLD)
    s_heading = S("heading", fontName=BOLD, fontSize=12, textColor=BRAND_GREEN,
                  spaceBefore=12, spaceAfter=4)
    s_sub     = S("sub",     fontName=BOLD, fontSize=10.5, textColor=BRAND_GREEN,
                  spaceBefore=8, spaceAfter=4)
    s_italic  = S("italic",  fontName=ITALIC, fontSize=9.5, textColor=colors.grey)
    s_sig     = S("sig",     fontName=REG, fontSize=9, leading=14)

    story = []

    def heading(txt):
        story.append(Paragraph(txt, s_heading))
        story.append(HRFlowable(width="100%", thickness=0.8,
                                color=BRAND_GOLD, spaceAfter=5))

    # ── 1. Greeting ────────────────────────────────────────────────────────
    client = data.get("client_name", "").strip() or "___________________"
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Уважаеми/а <b>{client}</b>,", s_body))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "Благодарим Ви за интереса към Lozenets Lounge. "
        "Представяме Ви следната оферта за вашето събитие:",
        s_body,
    ))
    story.append(Spacer(1, 10))

    # ── 2. Event description ───────────────────────────────────────────────
    heading("2. Описание на събитие")
    desc = data.get("event_description", "").strip()
    for line in (desc.splitlines() if desc else ["…"]):
        if line.strip():
            story.append(Paragraph(line.strip(), s_body if desc else s_italic))
    story.append(Spacer(1, 6))

    # ── 2.1 What's included ────────────────────────────────────────────────
    story.append(Paragraph("2.1. Какво е включено:", s_sub))
    items = [i.strip() for i in data.get("included_items", []) if i.strip()]
    if items:
        for item in items:
            story.append(Paragraph(f"● {item}", s_body))
    else:
        story.append(Paragraph("● …", s_italic))
    story.append(Spacer(1, 10))

    # ── 3. Pricing ─────────────────────────────────────────────────────────
    heading("3. Цена")
    col_w = [5.5 * cm, 2.8 * cm, 3.0 * cm, 3.2 * cm, 2.5 * cm]

    tbl_data = [[
        Paragraph("<b>Описание</b>",                    s_bold),
        Paragraph("<b>Цена / час</b>",                  s_bold),
        Paragraph("<b>Продължителност</b>",              s_bold),
        Paragraph("<b>Такси / Отстъпки / Други</b>",    s_bold),
        Paragraph("<b>Общо</b>",                        s_bold),
    ]]

    subtotal = 0.0
    for i, row in enumerate(data.get("price_rows", [])):
        raw_total = str(row.get("total", "")).strip()
        try:
            subtotal += float(raw_total.replace("€", "").replace(",", ".").strip())
        except ValueError:
            pass
        total_str = (f"€ {raw_total}" if raw_total and not raw_total.startswith("€")
                     else raw_total)
        rs = S(f"rs{i}", fontName=REG, fontSize=10, leading=13, spaceAfter=0)
        tbl_data.append([
            Paragraph(row.get("description",    ""), rs),
            Paragraph(row.get("price_per_hour", ""), rs),
            Paragraph(row.get("duration",       ""), rs),
            Paragraph(row.get("fees",           ""), rs),
            Paragraph(total_str,                     rs),
        ])

    vat = data.get("total_vat", "").strip()
    if not vat and subtotal:
        vat = f"{subtotal:.2f}"
    vat_str = f"€ {vat}" if vat and not vat.startswith("€") else (vat or "€ ___")

    tbl_data.append([
        Paragraph("<b>Общо (вкл. ДДС)</b>", s_bold),
        "", "", "",
        Paragraph(f"<b>{vat_str}</b>", s_bold),
    ])

    alternating = [
        ("BACKGROUND", (0, r), (-1, r), ROW_TINT)
        for r in range(2, len(tbl_data) - 1, 2)
    ]

    tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0),  (-1, 0),  BRAND_GREEN),
        ("TEXTCOLOR",     (0, 0),  (-1, 0),  WHITE),
        ("LINEBELOW",     (0, 0),  (-1, 0),  1.0, BRAND_GOLD),
        *alternating,
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#DFF0EE")),
        ("LINEABOVE",     (0, -1), (-1, -1), 1.0, BRAND_GOLD),
        ("SPAN",          (0, -1), (3,  -1)),
        ("GRID",          (0, 0),  (-1, -1), 0.3, MID_GREY),
        ("VALIGN",        (0, 0),  (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0),  (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0),  (-1, -1), 5),
        ("LEFTPADDING",   (0, 0),  (-1, -1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 14))

    # ── 4. Additional services ─────────────────────────────────────────────
    heading("4. Допълнителни Услуги")
    service_defs = [
        ("bar",        "Бар и пакет с напитки",                      "цена при запитване"),
        ("catering",   "Кетъринг / бюфет",                           "цена при запитване"),
        ("flowers",    "Флорална декорация",                          "цена при запитване"),
        ("sound",      "Ъпгрейд на професионална озвучителна система","цена при запитване"),
        ("photo",      "Фотография / видеозаснемане",                 "цена при запитване"),
        ("extra_time", "Удължено време за подготовка",                "€50 / час"),
    ]
    services  = data.get("additional_services", {})
    any_shown = False
    for key, label, price in service_defs:
        svc = services.get(key, {})
        if svc.get("selected"):
            any_shown = True
            note_part = f" — {svc['note']}" if svc.get("note", "").strip() else ""
            story.append(Paragraph(
                f"✓  <b>{label}</b>  "
                f"<font color='#888888'>({price})</font>{note_part}",
                s_body,
            ))
    if not any_shown:
        story.append(Paragraph("Не са избрани допълнителни услуги.", s_italic))
    story.append(Spacer(1, 12))

    # ── 5. Terms ───────────────────────────────────────────────────────────
    heading("5. Условия")
    terms = [
        "За потвърждаване на резервацията се изисква 50% депозит. "
        "Оставащата сума се заплаща 7 дни преди събитието.",
        "При анулация, направена повече от 14 дни преди събитието, депозитът се "
        "възстановява изцяло. При анулация в рамките на 14 дни преди събитието "
        "депозитът не подлежи на възстановяване.",
        "Всякакви щети по обекта или оборудването, причинени по време на събитието, "
        "са отговорност на клиента.",
        "След 23:00 ч. се прилагат ограничения за шума. Lozenets Lounge си запазва "
        "правото да следи за спазването им.",
        "Внасянето на външни храни и напитки подлежи на предварителна уговорка.",
    ]
    for i, term in enumerate(terms, 1):
        story.append(Paragraph(f"{i}.  {term}", s_body))
    story.append(Spacer(1, 12))

    # ── 6. Validity ────────────────────────────────────────────────────────
    heading("6. Валидност")
    valid_until = data.get("valid_until", "").strip() or "_____________________________"
    story.append(Paragraph(
        f"Офертата е валидна до: <b>{valid_until}</b>   "
        "След тази дата, цената може да подлежи на промени.",
        s_body,
    ))
    story.append(Spacer(1, 18))

    # ── 7. Signatures ──────────────────────────────────────────────────────
    heading("7. Съгласие и подписи")
    sig_tbl = Table(
        [
            [Paragraph("Lozenets Lounge (Подпис и Дата)", s_sig),
             Paragraph("Клиент (Подпис и Дата)", s_sig)],
            [Paragraph("____________________________", s_sig),
             Paragraph("____________________________", s_sig)],
        ],
        colWidths=[9 * cm, 9 * cm],
    )
    sig_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_tbl)

    doc.build(story)
