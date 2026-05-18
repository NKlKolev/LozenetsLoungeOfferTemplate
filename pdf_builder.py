#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF generation for Lozenets Lounge offer documents.
Fonts are bundled in the fonts/ subdirectory so the module works
on Streamlit Cloud (Linux), macOS, and Windows without any system fonts.
"""

import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF generation for Lozenets Lounge offer documents.
Fonts are bundled in the fonts/ subdirectory so the module works
on Streamlit Cloud (Linux), macOS, and Windows without any system fonts.
"""

import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Paths ──────────────────────────────────────────────────────────────────
_DIR   = os.path.dirname(os.path.abspath(__file__))
_FONTS = os.path.join(_DIR, "fonts")
_LOGO_ICON  = os.path.join(_DIR, "logo_icon.png")
_LOGO_HOUSE = os.path.join(_DIR, "logo_house.png")

# ── Font registration ──────────────────────────────────────────────────────
# Priority order: bundled DejaVu → Linux system DejaVu → macOS Arial → macOS Tahoma
_CANDIDATES = [
    (
        os.path.join(_FONTS, "DejaVuSans.ttf"),
        os.path.join(_FONTS, "DejaVuSans-Bold.ttf"),
        os.path.join(_FONTS, "DejaVuSans-Oblique.ttf"),
        os.path.join(_FONTS, "DejaVuSans-BoldOblique.ttf"),
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    ),
    (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
    ),
    (
        "/System/Library/Fonts/Supplemental/Tahoma.ttf",
        "/System/Library/Fonts/Supplemental/Tahoma Bold.ttf",
        None,
        None,
    ),
]

REG = BOLD = ITALIC = BOLD_ITALIC = None

for _r, _b, _i, _bi in _CANDIDATES:
    if os.path.exists(_r) and os.path.exists(_b):
        pdfmetrics.registerFont(TTFont("_Reg",  _r))
        pdfmetrics.registerFont(TTFont("_Bold", _b))
        if _i  and os.path.exists(_i):  pdfmetrics.registerFont(TTFont("_Ital",   _i))
        if _bi and os.path.exists(_bi): pdfmetrics.registerFont(TTFont("_BoldI",  _bi))
        REG        = "_Reg"
        BOLD       = "_Bold"
        ITALIC     = "_Ital"  if (_i  and os.path.exists(_i))  else "_Reg"
        BOLD_ITALIC= "_BoldI" if (_bi and os.path.exists(_bi)) else "_Bold"
        break

if REG is None:
    raise RuntimeError(
        "No Cyrillic font found. "
        "Make sure the fonts/ directory contains DejaVuSans.ttf and DejaVuSans-Bold.ttf."
    )

# ── Brand colours ──────────────────────────────────────────────────────────
C_GREEN  = colors.HexColor("#19514A")
C_GOLD   = colors.HexColor("#E9D281")
C_CREAM  = colors.HexColor("#F5F0E8")
C_ROWTINT= colors.HexColor("#EAF1F0")
C_GREY   = colors.HexColor("#CCCCCC")
C_WHITE  = colors.white

# ── Page geometry ──────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN   = 2.0 * cm
HEADER_H = 3.4 * cm
FOOTER_H = 2.6 * cm


# ══════════════════════════════════════════════════════════════════════════
#  HEADER / FOOTER  (drawn on every page by ReportLab canvas)
# ══════════════════════════════════════════════════════════════════════════
def _draw_header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # ── Header ─────────────────────────────────────────────────────────────
    # Green background
    canvas.setFillColor(C_GREEN)
    canvas.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)

    # Gold accent line below header
    canvas.setFillColor(C_GOLD)
    canvas.rect(0, h - HEADER_H - 0.10 * cm, w, 0.10 * cm, fill=1, stroke=0)

    # Logo image centred — no extra text
    logo = _LOGO_ICON if os.path.exists(_LOGO_ICON) else (
           _LOGO_HOUSE if os.path.exists(_LOGO_HOUSE) else None)
    if logo:
        lh = HEADER_H * 0.82
        lw = lh
        lx = (w - lw) / 2
        ly = h - HEADER_H + (HEADER_H - lh) / 2
        try:
            canvas.drawImage(logo, lx, ly, width=lw, height=lh,
                             mask="auto", preserveAspectRatio=True)
        except Exception:
            pass

    # ── Footer ─────────────────────────────────────────────────────────────
    # Green background
    canvas.setFillColor(C_GREEN)
    canvas.rect(0, 0, w, FOOTER_H, fill=1, stroke=0)

    # Gold accent line above footer
    canvas.setFillColor(C_GOLD)
    canvas.rect(0, FOOTER_H, w, 0.09 * cm, fill=1, stroke=0)

    # Logo in footer — right side
    if logo:
        fh = FOOTER_H * 0.82
        fw = fh
        fy = (FOOTER_H - fh) / 2
        fx = w - MARGIN - fw
        try:
            canvas.drawImage(logo, fx, fy, width=fw, height=fh,
                             mask="auto", preserveAspectRatio=True)
        except Exception:
            pass

    # Contact text — left side
    canvas.setFont(REG, 7.5)
    canvas.setFillColor(C_WHITE)
    canvas.drawString(MARGIN, FOOTER_H * 0.65,
                      "Instagram: @lozenets_lounge   |   Facebook: Lozenets Lounge")
    canvas.drawString(MARGIN, FOOTER_H * 0.30,
                      "Website: lozenetslounge.eu   |   София, Лозенец, ул. Кръстьо Сарафов 22")

    canvas.restoreState()


# ══════════════════════════════════════════════════════════════════════════
#  MAIN PDF BUILDER
# ══════════════════════════════════════════════════════════════════════════
def build_pdf(data: dict, output):
    """
    Build the offer PDF.
    `output` — file path (str) or BytesIO object.
    `data` keys:
        client_name, event_description, included_items (list),
        price_rows (list of dicts), additional_services (dict),
        valid_until (str), subtotal_str, vat_str, total_vat_str
    """

    doc = BaseDocTemplate(
        output,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HEADER_H + 0.5 * cm,
        bottomMargin=FOOTER_H + 0.5 * cm,
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        PAGE_W - 2 * MARGIN,
        PAGE_H - HEADER_H - FOOTER_H - 1.0 * cm,
        id="main",
    )
    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=_draw_header_footer)
    ])

    # ── Paragraph style factory ────────────────────────────────────────────
    def S(name, **kw):
        base = dict(fontName=REG, fontSize=10, leading=14, spaceAfter=3,
                    encoding="utf-8")
        base.update(kw)
        return ParagraphStyle(name, **base)

    s_body    = S("body")
    s_bold    = S("bold",    fontName=BOLD)
    s_hdr     = S("hdr",     fontName=BOLD, fontSize=9,   textColor=C_WHITE,
                  leading=13, spaceAfter=0)
    s_heading = S("heading", fontName=BOLD, fontSize=12,  textColor=C_GREEN,
                  spaceBefore=12, spaceAfter=4)
    s_sub     = S("sub",     fontName=BOLD, fontSize=10.5,textColor=C_GREEN,
                  spaceBefore=8,  spaceAfter=4)
    s_italic  = S("italic",  fontName=ITALIC, fontSize=9.5, textColor=colors.grey)
    s_small   = S("small",   fontName=REG,  fontSize=9,   textColor=colors.grey, leading=13)
    s_sig     = S("sig",     fontName=REG,  fontSize=9,   leading=14)
    s_sum     = S("sum",     fontName=REG,  fontSize=9.5, leading=13, spaceAfter=0)
    s_total   = S("total",   fontName=BOLD, fontSize=10,  leading=13, spaceAfter=0)

    story = []

    def heading(txt):
        story.append(Paragraph(txt, s_heading))
        story.append(HRFlowable(width="100%", thickness=0.8,
                                color=C_GOLD, spaceAfter=5))

    # ── Greeting ───────────────────────────────────────────────────────────
    client = data.get("client_name", "").strip() or "___________________"
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Уважаеми/а <b>{client}</b>,", s_body))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "Благодарим Ви за интереса към Lozenets Lounge. "
        "Представяме Ви следната оферта за Вашето събитие:",
        s_body,
    ))
    story.append(Spacer(1, 10))

    # ── 2. Event description ───────────────────────────────────────────────
    heading("2. Описание на събитие")
    desc = (data.get("event_description") or "").strip()
    lines = desc.splitlines() if desc else []
    for line in lines:
        if line.strip():
            story.append(Paragraph(line.strip(), s_body))
    if not lines:
        story.append(Paragraph("…", s_italic))
    story.append(Spacer(1, 6))

    # ── 2.1 What's included ────────────────────────────────────────────────
    story.append(Paragraph("2.1. Какво е включено:", s_sub))
    items = [i.strip() for i in data.get("included_items", []) if i.strip()]
    if items:
        for item in items:
            story.append(Paragraph(f"●  {item}", s_body))
    else:
        story.append(Paragraph("●  …", s_italic))
    story.append(Spacer(1, 10))

    # ── 3. Pricing table ───────────────────────────────────────────────────
    heading("3. Цена")

    col_w = [5.5 * cm, 2.8 * cm, 3.0 * cm, 3.2 * cm, 2.5 * cm]

    # Header row — uses s_hdr (white text on green bg)
    tbl = [[
        Paragraph("Описание",               s_hdr),
        Paragraph("Цена / час",             s_hdr),
        Paragraph("Продължителност",         s_hdr),
        Paragraph("Отстъпка",                s_hdr),
        Paragraph("Общо",                   s_hdr),
    ]]

    for i, row in enumerate(data.get("price_rows", [])):
        rs = S(f"rs{i}", fontName=REG, fontSize=10, leading=13, spaceAfter=0)
        tbl.append([
            Paragraph(str(row.get("description",    "") or ""), rs),
            Paragraph(str(row.get("price_per_hour", "") or ""), rs),
            Paragraph(str(row.get("duration",       "") or ""), rs),
            Paragraph(str(row.get("fees",           "") or ""), rs),
            Paragraph(str(row.get("total",          "") or ""), rs),
        ])

    n = len(tbl)   # number of rows before summary row

    # Single summary row — total already includes VAT
    tbl += [
        [Paragraph("Обща цена (вкл. ДДС)", s_total), "", "", "",
         Paragraph(data.get("total_vat_str", "—"), s_total)],
    ]

    alternating = [
        ("BACKGROUND", (0, r), (-1, r), C_ROWTINT)
        for r in range(2, n, 2)
    ]

    table = Table(tbl, colWidths=col_w, repeatRows=1)
    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0),  C_GREEN),
        ("LINEBELOW",     (0, 0), (-1, 0),  1.0, C_GOLD),
        # Alternating data rows
        *alternating,
        # Total row
        ("BACKGROUND",    (0, n), (-1, n),  colors.HexColor("#D4EAE7")),
        ("LINEABOVE",     (0, n), (-1, n),  1.0, C_GOLD),
        ("SPAN",          (0, n), (3,  n)),
        # Grid & padding
        ("GRID",          (0, 0), (-1, -1), 0.3, C_GREY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 14))

    # ── 4. Additional services ─────────────────────────────────────────────
    heading("4. Допълнителни Услуги")
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
            story.append(Paragraph(
                f"✓  <b>{label}</b>  "
                f"<font color='#888888'>({price})</font>{note_part}",
                s_body,
            ))
    if not any_shown:
        story.append(Paragraph("Не са избрани допълнителни услуги.", s_italic))
    story.append(Spacer(1, 12))

    # ── 5. Terms & Conditions ──────────────────────────────────────────────
    heading("5. Условия")
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
        story.append(Paragraph(f"{i}.  {term}", s_body))
    story.append(Spacer(1, 12))

    # ── 6. Validity ────────────────────────────────────────────────────────
    heading("6. Валидност")
    valid_until = (data.get("valid_until") or "").strip() or "_____________________________"
    story.append(Paragraph(
        f"Офертата е валидна до: <b>{valid_until}</b>.",
        s_body,
    ))
    story.append(Spacer(1, 18))

    # ── 7. Signatures ──────────────────────────────────────────────────────
    heading("7. Съгласие и подписи")
    sig_table = Table(
        [
            [Paragraph("Даниела Боянова-Колева (Подпис и Дата)", s_sig),
             Paragraph("Клиент (Подпис и Дата)", s_sig)],
            [Paragraph("____________________________", s_sig),
             Paragraph("____________________________", s_sig)],
        ],
        colWidths=[9 * cm, 9 * cm],
    )
    sig_table.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_table)

    doc.build(story)

# ── Paths ──────────────────────────────────────────────────────────────────
_DIR   = os.path.dirname(os.path.abspath(__file__))
_FONTS = os.path.join(_DIR, "fonts")
_LOGO_ICON  = os.path.join(_DIR, "logo_icon.png")
_LOGO_HOUSE = os.path.join(_DIR, "logo_house.png")

# ── Font registration ──────────────────────────────────────────────────────
# Priority order: bundled DejaVu → Linux system DejaVu → macOS Arial → macOS Tahoma
_CANDIDATES = [
    (
        os.path.join(_FONTS, "DejaVuSans.ttf"),
        os.path.join(_FONTS, "DejaVuSans-Bold.ttf"),
        os.path.join(_FONTS, "DejaVuSans-Oblique.ttf"),
        os.path.join(_FONTS, "DejaVuSans-BoldOblique.ttf"),
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    ),
    (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
    ),
    (
        "/System/Library/Fonts/Supplemental/Tahoma.ttf",
        "/System/Library/Fonts/Supplemental/Tahoma Bold.ttf",
        None,
        None,
    ),
]

REG = BOLD = ITALIC = BOLD_ITALIC = None

for _r, _b, _i, _bi in _CANDIDATES:
    if os.path.exists(_r) and os.path.exists(_b):
        pdfmetrics.registerFont(TTFont("_Reg",  _r))
        pdfmetrics.registerFont(TTFont("_Bold", _b))
        if _i  and os.path.exists(_i):  pdfmetrics.registerFont(TTFont("_Ital",   _i))
        if _bi and os.path.exists(_bi): pdfmetrics.registerFont(TTFont("_BoldI",  _bi))
        REG        = "_Reg"
        BOLD       = "_Bold"
        ITALIC     = "_Ital"  if (_i  and os.path.exists(_i))  else "_Reg"
        BOLD_ITALIC= "_BoldI" if (_bi and os.path.exists(_bi)) else "_Bold"
        break

if REG is None:
    raise RuntimeError(
        "No Cyrillic font found. "
        "Make sure the fonts/ directory contains DejaVuSans.ttf and DejaVuSans-Bold.ttf."
    )

# ── Brand colours ──────────────────────────────────────────────────────────
C_GREEN  = colors.HexColor("#19514A")
C_GOLD   = colors.HexColor("#E9D281")
C_CREAM  = colors.HexColor("#F5F0E8")
C_ROWTINT= colors.HexColor("#EAF1F0")
C_GREY   = colors.HexColor("#CCCCCC")
C_WHITE  = colors.white

# ── Page geometry ──────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN   = 2.0 * cm
HEADER_H = 3.4 * cm
FOOTER_H = 2.6 * cm


# ══════════════════════════════════════════════════════════════════════════
#  HEADER / FOOTER  (drawn on every page by ReportLab canvas)
# ══════════════════════════════════════════════════════════════════════════
def _draw_header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # ── Header ─────────────────────────────────────────────────────────────
    # Green background
    canvas.setFillColor(C_GREEN)
    canvas.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)

    # Gold accent line below header
    canvas.setFillColor(C_GOLD)
    canvas.rect(0, h - HEADER_H - 0.10 * cm, w, 0.10 * cm, fill=1, stroke=0)

    # Logo image centred — no extra text
    logo = _LOGO_ICON if os.path.exists(_LOGO_ICON) else (
           _LOGO_HOUSE if os.path.exists(_LOGO_HOUSE) else None)
    if logo:
        lh = HEADER_H * 0.82
        lw = lh
        lx = (w - lw) / 2
        ly = h - HEADER_H + (HEADER_H - lh) / 2
        try:
            canvas.drawImage(logo, lx, ly, width=lw, height=lh,
                             mask="auto", preserveAspectRatio=True)
        except Exception:
            pass

    # ── Footer ─────────────────────────────────────────────────────────────
    # Green background
    canvas.setFillColor(C_GREEN)
    canvas.rect(0, 0, w, FOOTER_H, fill=1, stroke=0)

    # Gold accent line above footer
    canvas.setFillColor(C_GOLD)
    canvas.rect(0, FOOTER_H, w, 0.09 * cm, fill=1, stroke=0)

    # Logo in footer — right side
    if logo:
        fh = FOOTER_H * 0.82
        fw = fh
        fy = (FOOTER_H - fh) / 2
        fx = w - MARGIN - fw
        try:
            canvas.drawImage(logo, fx, fy, width=fw, height=fh,
                             mask="auto", preserveAspectRatio=True)
        except Exception:
            pass

    # Contact text — left side
    canvas.setFont(REG, 7.5)
    canvas.setFillColor(C_WHITE)
    canvas.drawString(MARGIN, FOOTER_H * 0.65,
                      "Instagram: @lozenets_lounge   |   Facebook: Lozenets Lounge")
    canvas.drawString(MARGIN, FOOTER_H * 0.30,
                      "Website: lozenetslounge.eu   |   София, Лозенец, ул. Кръстьо Сарафов 22")

    canvas.restoreState()


# ══════════════════════════════════════════════════════════════════════════
#  MAIN PDF BUILDER
# ══════════════════════════════════════════════════════════════════════════
def build_pdf(data: dict, output):
    """
    Build the offer PDF.
    `output` — file path (str) or BytesIO object.
    `data` keys:
        client_name, event_description, included_items (list),
        price_rows (list of dicts), additional_services (dict),
        valid_until (str), subtotal_str, vat_str, total_vat_str
    """

    doc = BaseDocTemplate(
        output,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HEADER_H + 0.5 * cm,
        bottomMargin=FOOTER_H + 0.5 * cm,
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        PAGE_W - 2 * MARGIN,
        PAGE_H - HEADER_H - FOOTER_H - 1.0 * cm,
        id="main",
    )
    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=_draw_header_footer)
    ])

    # ── Paragraph style factory ────────────────────────────────────────────
    def S(name, **kw):
        base = dict(fontName=REG, fontSize=10, leading=14, spaceAfter=3,
                    encoding="utf-8")
        base.update(kw)
        return ParagraphStyle(name, **base)

    s_body    = S("body")
    s_bold    = S("bold",    fontName=BOLD)
    s_hdr     = S("hdr",     fontName=BOLD, fontSize=9,   textColor=C_WHITE,
                  leading=13, spaceAfter=0)
    s_heading = S("heading", fontName=BOLD, fontSize=12,  textColor=C_GREEN,
                  spaceBefore=12, spaceAfter=4)
    s_sub     = S("sub",     fontName=BOLD, fontSize=10.5,textColor=C_GREEN,
                  spaceBefore=8,  spaceAfter=4)
    s_italic  = S("italic",  fontName=ITALIC, fontSize=9.5, textColor=colors.grey)
    s_small   = S("small",   fontName=REG,  fontSize=9,   textColor=colors.grey, leading=13)
    s_sig     = S("sig",     fontName=REG,  fontSize=9,   leading=14)
    s_sum     = S("sum",     fontName=REG,  fontSize=9.5, leading=13, spaceAfter=0)
    s_total   = S("total",   fontName=BOLD, fontSize=10,  leading=13, spaceAfter=0)

    story = []

    def heading(txt):
        story.append(Paragraph(txt, s_heading))
        story.append(HRFlowable(width="100%", thickness=0.8,
                                color=C_GOLD, spaceAfter=5))

    # ── Greeting ───────────────────────────────────────────────────────────
    client = data.get("client_name", "").strip() or "___________________"
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Уважаеми/а <b>{client}</b>,", s_body))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "Благодарим Ви за интереса към Lozenets Lounge. "
        "Представяме Ви следната оферта за Вашето събитие:",
        s_body,
    ))
    story.append(Spacer(1, 10))

    # ── 2. Event description ───────────────────────────────────────────────
    heading("2. Описание на събитие")
    desc = (data.get("event_description") or "").strip()
    lines = desc.splitlines() if desc else []
    for line in lines:
        if line.strip():
            story.append(Paragraph(line.strip(), s_body))
    if not lines:
        story.append(Paragraph("…", s_italic))
    story.append(Spacer(1, 6))

    # ── 2.1 What's included ────────────────────────────────────────────────
    story.append(Paragraph("2.1. Какво е включено:", s_sub))
    items = [i.strip() for i in data.get("included_items", []) if i.strip()]
    if items:
        for item in items:
            story.append(Paragraph(f"●  {item}", s_body))
    else:
        story.append(Paragraph("●  …", s_italic))
    story.append(Spacer(1, 10))

    # ── 3. Pricing table ───────────────────────────────────────────────────
    heading("3. Цена")

    col_w = [5.5 * cm, 2.8 * cm, 3.0 * cm, 3.2 * cm, 2.5 * cm]

    # Header row — uses s_hdr (white text on green bg)
    tbl = [[
        Paragraph("Описание",               s_hdr),
        Paragraph("Цена / час",             s_hdr),
        Paragraph("Продължителност",         s_hdr),
        Paragraph("Отстъпка",                s_hdr),
        Paragraph("Общо",                   s_hdr),
    ]]

    for i, row in enumerate(data.get("price_rows", [])):
        rs = S(f"rs{i}", fontName=REG, fontSize=10, leading=13, spaceAfter=0)
        tbl.append([
            Paragraph(str(row.get("description",    "") or ""), rs),
            Paragraph(str(row.get("price_per_hour", "") or ""), rs),
            Paragraph(str(row.get("duration",       "") or ""), rs),
            Paragraph(str(row.get("fees",           "") or ""), rs),
            Paragraph(str(row.get("total",          "") or ""), rs),
        ])

    n = len(tbl)   # number of rows before summary row

    # Single summary row — total already includes VAT
    tbl += [
        [Paragraph("Обща цена (вкл. ДДС)", s_total), "", "", "",
         Paragraph(data.get("total_vat_str", "—"), s_total)],
    ]

    alternating = [
        ("BACKGROUND", (0, r), (-1, r), C_ROWTINT)
        for r in range(2, n, 2)
    ]

    table = Table(tbl, colWidths=col_w, repeatRows=1)
    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0),  C_GREEN),
        ("LINEBELOW",     (0, 0), (-1, 0),  1.0, C_GOLD),
        # Alternating data rows
        *alternating,
        # Total row
        ("BACKGROUND",    (0, n), (-1, n),  colors.HexColor("#D4EAE7")),
        ("LINEABOVE",     (0, n), (-1, n),  1.0, C_GOLD),
        ("SPAN",          (0, n), (3,  n)),
        # Grid & padding
        ("GRID",          (0, 0), (-1, -1), 0.3, C_GREY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 14))

    # ── 4. Additional services ─────────────────────────────────────────────
    heading("4. Допълнителни Услуги")
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
            story.append(Paragraph(
                f"✓  <b>{label}</b>  "
                f"<font color='#888888'>({price})</font>{note_part}",
                s_body,
            ))
    if not any_shown:
        story.append(Paragraph("Не са избрани допълнителни услуги.", s_italic))
    story.append(Spacer(1, 12))

    # ── 5. Terms & Conditions ──────────────────────────────────────────────
    heading("5. Условия")
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
        story.append(Paragraph(f"{i}.  {term}", s_body))
    story.append(Spacer(1, 12))

    # ── 6. Validity ────────────────────────────────────────────────────────
    heading("6. Валидност")
    valid_until = (data.get("valid_until") or "").strip() or "_____________________________"
    story.append(Paragraph(
        f"Офертата е валидна до: <b>{valid_until}</b>.",
        s_body,
    ))
    story.append(Spacer(1, 18))

    # ── 7. Signatures ──────────────────────────────────────────────────────
    heading("7. Съгласие и подписи")
    sig_table = Table(
        [
            [Paragraph("Даниела Боянова-Колева (Подпис и Дата)", s_sig),
             Paragraph("Клиент (Подпис и Дата)", s_sig)],
            [Paragraph("____________________________", s_sig),
             Paragraph("____________________________", s_sig)],
        ],
        colWidths=[9 * cm, 9 * cm],
    )
    sig_table.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_table)

    doc.build(story)
