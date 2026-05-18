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
# Bundled DejaVu fonts ship with the project (fonts/ directory) so the app
# works identically on macOS, Linux (Streamlit Cloud), and Windows.
_HERE_FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

_FONT_CANDIDATES = [
    # 1. Bundled DejaVu (always present in repo — preferred)
    (
        os.path.join(_HERE_FONTS, "DejaVuSans.ttf"),
        os.path.join(_HERE_FONTS, "DejaVuSans-Bold.ttf"),
        os.path.join(_HERE_FONTS, "DejaVuSans-Oblique.ttf"),
        os.path.join(_HERE_FONTS, "DejaVuSans-BoldOblique.ttf"),
    ),
    # 2. Linux system DejaVu (Ubuntu / Streamlit Cloud fallback)
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    ),
    # 3. macOS Arial
    (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
    ),
    # 4. macOS Tahoma
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
    raise RuntimeError(
        "No Cyrillic font found. Expected fonts/DejaVuSans.ttf in the project directory."
    )

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
    s_hdr     = S("hdr",     fontName=BOLD,   fontSize=9,    textColor=WHITE,       leading=13, spaceAfter=0)
    s_heading = S("heading", fontName=BOLD,   fontSize=12,   textColor=BRAND_GREEN, spaceBefore=12, spaceAfter=4)
    s_sub     = S("sub",     fontName=BOLD,   fontSize=10.5, textColor=BRAND_GREEN, spaceBefore=8,  spaceAfter=4)
    s_italic  = S("italic",  fontName=ITALIC, fontSize=9.5,  textColor=colors.grey)
    s_sig     = S("sig",     fontName=REG,    fontSize=9,    leading=14)

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
        Paragraph("Описание",                    s_hdr),
        Paragraph("Цена / час",                  s_hdr),
        Paragraph("Продължителност",              s_hdr),
        Paragraph("Такси / Отстъпки / Други",    s_hdr),
        Paragraph("Общо",                        s_hdr),
    ]]

    for i, row in enumerate(data.get("price_rows", [])):
        rs = S(f"rs{i}", fontName=REG, fontSize=10, leading=13, spaceAfter=0)
        tbl_data.append([
            Paragraph(str(row.get("description",    "")), rs),
            Paragraph(str(row.get("price_per_hour", "")), rs),
            Paragraph(str(row.get("duration",       "")), rs),
            Paragraph(str(row.get("fees",           "")), rs),
            Paragraph(str(row.get("total",          "")), rs),
        ])

    # Summary rows — values already calculated by the app
    subtotal_str  = data.get("subtotal_str",  "€ 0.00")
    vat_str       = data.get("vat_str",       "€ 0.00")
    total_vat_str = data.get("total_vat_str", "€ 0.00")

    s_sum = S("sum", fontName=REG,  fontSize=9.5, leading=13, spaceAfter=0)
    s_tot = S("tot", fontName=BOLD, fontSize=10,  leading=13, spaceAfter=0)

    n_data_rows = len(tbl_data)   # header + data rows (before summary rows)
    tbl_data += [
        [Paragraph("Междинна сума",  s_sum), "", "", "", Paragraph(subtotal_str,  s_sum)],
        [Paragraph("ДДС 20%",        s_sum), "", "", "", Paragraph(vat_str,       s_sum)],
        [Paragraph("Общо (вкл. ДДС)", s_tot), "", "", "", Paragraph(total_vat_str, s_tot)],
    ]

    alternating = [
        ("BACKGROUND", (0, r), (-1, r), ROW_TINT)
        for r in range(2, n_data_rows, 2)
    ]

    tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        # Header row — green bg, white text via s_hdr paragraph style
        ("BACKGROUND",    (0, 0),  (-1, 0),          BRAND_GREEN),
        ("LINEBELOW",     (0, 0),  (-1, 0),          1.0, BRAND_GOLD),
        # Alternating data rows
        *alternating,
        # Summary rows
        ("BACKGROUND",    (0, n_data_rows),   (-1, n_data_rows),   colors.HexColor("#EAF1F0")),
        ("BACKGROUND",    (0, n_data_rows+1), (-1, n_data_rows+1), colors.HexColor("#EAF1F0")),
        ("BACKGROUND",    (0, n_data_rows+2), (-1, n_data_rows+2), colors.HexColor("#D4EAE7")),
        ("LINEABOVE",     (0, n_data_rows),   (-1, n_data_rows),   0.6, MID_GREY),
        ("LINEABOVE",     (0, n_data_rows+2), (-1, n_data_rows+2), 1.0, BRAND_GOLD),
        # Span label columns for summary rows
        ("SPAN",          (0, n_data_rows),   (3, n_data_rows)),
        ("SPAN",          (0, n_data_rows+1), (3, n_data_rows+1)),
        ("SPAN",          (0, n_data_rows+2), (3, n_data_rows+2)),
        # Grid & padding
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
