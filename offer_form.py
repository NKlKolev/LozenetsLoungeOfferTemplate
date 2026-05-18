#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, Table, TableStyle, HRFlowable, Image as RLImage
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Font Registration ──────────────────────────────────────────────────────
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
for _reg, _bold, _ital, _boldital in _FONT_CANDIDATES:
    if os.path.exists(_reg) and os.path.exists(_bold):
        pdfmetrics.registerFont(TTFont("OfferReg",      _reg))
        pdfmetrics.registerFont(TTFont("OfferBold",     _bold))
        if _ital and os.path.exists(_ital):
            pdfmetrics.registerFont(TTFont("OfferItalic", _ital))
        if _boldital and os.path.exists(_boldital):
            pdfmetrics.registerFont(TTFont("OfferBoldItalic", _boldital))
        REG        = "OfferReg"
        BOLD       = "OfferBold"
        ITALIC     = "OfferItalic"     if _ital     else "OfferReg"
        BOLD_ITALIC= "OfferBoldItalic" if _boldital else "OfferBold"
        break

if not REG:
    raise RuntimeError("No suitable Cyrillic-capable font found (Arial or Tahoma).")

# ── Brand colours ──────────────────────────────────────────────────────────
#  Exact values sampled from the official logo assets
BRAND_GREEN  = colors.HexColor("#19514A")   # primary dark green
BRAND_GOLD   = colors.HexColor("#E9D281")   # gold accent
BRAND_CREAM  = colors.HexColor("#F5F0E8")   # warm off-white for alternating rows
MID_GREY     = colors.HexColor("#CCCCCC")
WHITE        = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm

# Logo path (same folder as this script)
_HERE      = os.path.dirname(os.path.abspath(__file__))
LOGO_HOUSE = os.path.join(_HERE, "logo_house.png")   # transparent house PNG
LOGO_ICON  = os.path.join(_HERE, "logo_icon.png")    # square icon (fallback)


# ══════════════════════════════════════════════════════════════════════════
#  PDF BUILDER
# ══════════════════════════════════════════════════════════════════════════

def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # ── Header background ──────────────────────────────────────────────────
    HEADER_H = 3.0 * cm
    canvas.setFillColor(BRAND_GREEN)
    canvas.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)

    # Gold accent line below header
    canvas.setFillColor(BRAND_GOLD)
    canvas.rect(0, h - HEADER_H - 0.10 * cm, w, 0.10 * cm, fill=1, stroke=0)

    # Logo (house illustration) on the left side of header
    logo_path = LOGO_HOUSE if os.path.exists(LOGO_HOUSE) else (
                LOGO_ICON  if os.path.exists(LOGO_ICON)  else None)
    if logo_path:
        logo_h = HEADER_H * 0.82
        logo_w = logo_h  # square
        try:
            canvas.drawImage(
                logo_path,
                MARGIN, h - HEADER_H + (HEADER_H - logo_h) / 2,
                width=logo_w, height=logo_h,
                mask="auto",
                preserveAspectRatio=True,
            )
            text_x = MARGIN + logo_w + 0.4 * cm
        except Exception:
            text_x = MARGIN
    else:
        text_x = MARGIN

    # "Lozenets Lounge" text
    canvas.setFont(BOLD, 17)
    canvas.setFillColor(WHITE)
    canvas.drawString(text_x, h - 1.55 * cm, "Lozenets Lounge")

    # "est. 1942" subtitle
    canvas.setFont(ITALIC, 8)
    canvas.setFillColor(BRAND_GOLD)
    canvas.drawString(text_x, h - 2.10 * cm, "est. 1942")

    # Website (right-aligned)
    canvas.setFont(REG, 7.5)
    canvas.setFillColor(BRAND_GOLD)
    canvas.drawRightString(w - MARGIN, h - 1.5 * cm, "lozenetslounge.eu")
    canvas.drawRightString(w - MARGIN, h - 2.0 * cm, "@lozenets_lounge")

    # ── Footer background ──────────────────────────────────────────────────
    FOOTER_H = 1.6 * cm
    canvas.setFillColor(BRAND_GREEN)
    canvas.rect(0, 0, w, FOOTER_H, fill=1, stroke=0)

    # Gold accent line above footer
    canvas.setFillColor(BRAND_GOLD)
    canvas.rect(0, FOOTER_H, w, 0.08 * cm, fill=1, stroke=0)

    # Footer text
    canvas.setFont(REG, 7.5)
    canvas.setFillColor(WHITE)
    canvas.drawString(
        MARGIN, 0.9 * cm,
        "Instagram: @lozenets_lounge   |   Facebook: Lozenets Lounge   |   Website: lozenetslounge.eu",
    )
    canvas.setFillColor(BRAND_GOLD)
    canvas.drawRightString(
        w - MARGIN, 0.9 * cm,
        "София, Лозенец, ул. Кръстьо Сарафов 22",
    )

    canvas.restoreState()


def build_pdf(data: dict, filepath: str):
    doc = BaseDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=3.6 * cm,
        bottomMargin=2.2 * cm,
    )

    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        PAGE_W - 2 * MARGIN, PAGE_H - 5.8 * cm,
        id="main",
    )
    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=_header_footer)
    ])

    # ── Paragraph styles ───────────────────────────────────────────────────
    def S(name, **kw):
        defaults = dict(fontName=REG, fontSize=10, leading=14, spaceAfter=4)
        defaults.update(kw)
        return ParagraphStyle(name, **defaults)

    s_body    = S("body")
    s_bold    = S("bold",    fontName=BOLD)
    s_heading = S("heading", fontName=BOLD, fontSize=12, textColor=BRAND_GREEN,
                  spaceBefore=14, spaceAfter=4)
    s_sub     = S("sub",     fontName=BOLD, fontSize=10.5, textColor=BRAND_GREEN,
                  spaceBefore=8, spaceAfter=4)
    s_italic  = S("italic",  fontName=ITALIC, fontSize=9.5, textColor=colors.grey)
    s_sig     = S("sig",     fontName=REG, fontSize=9, leading=12)

    story = []

    def heading(txt):
        story.append(Paragraph(txt, s_heading))
        story.append(HRFlowable(width="100%", thickness=0.8,
                                color=BRAND_GOLD, spaceAfter=6))

    def subheading(txt):
        story.append(Paragraph(txt, s_sub))

    # ── 1. Greeting ────────────────────────────────────────────────────────
    client = data.get("client_name", "").strip() or "___________________"
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Уважаеми/а <b>{client}</b>,", s_body))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Благодарим Ви за интереса към Lozenets Lounge. "
        "Представяме Ви следната оферта за вашето събитие:",
        s_body,
    ))
    story.append(Spacer(1, 10))

    # ── 2. Event description ───────────────────────────────────────────────
    heading("2. Описание на събитие")
    desc = data.get("event_description", "").strip()
    if desc:
        for line in desc.splitlines():
            if line.strip():
                story.append(Paragraph(line.strip(), s_body))
    else:
        story.append(Paragraph("…", s_italic))
    story.append(Spacer(1, 6))

    # ── 2.1 What's included ────────────────────────────────────────────────
    subheading("2.1. Какво е включено:")
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

    # Header row
    tbl_data = [[
        Paragraph("<b>Описание</b>",               s_bold),
        Paragraph("<b>Цена / час</b>",             s_bold),
        Paragraph("<b>Продължителност</b>",         s_bold),
        Paragraph("<b>Такси / Отстъпки / Други</b>", s_bold),
        Paragraph("<b>Общо</b>",                   s_bold),
    ]]

    subtotal = 0.0
    for i, row in enumerate(data.get("price_rows", [])):
        total_raw = row.get("total", "")
        try:
            subtotal += float(str(total_raw).replace("€", "").replace(",", ".").strip())
        except ValueError:
            pass
        total_display = (
            f"€ {total_raw}"
            if total_raw and not str(total_raw).startswith("€")
            else total_raw
        )
        row_style = S(f"row{i}", fontName=REG, fontSize=10, leading=14, spaceAfter=0)
        tbl_data.append([
            Paragraph(row.get("description",    ""), row_style),
            Paragraph(row.get("price_per_hour", ""), row_style),
            Paragraph(row.get("duration",       ""), row_style),
            Paragraph(row.get("fees",           ""), row_style),
            Paragraph(total_display or "",           row_style),
        ])

    vat_total = data.get("total_vat", "").strip()
    if not vat_total and subtotal:
        vat_total = f"{subtotal:.2f}"
    vat_display = (
        f"€ {vat_total}"
        if vat_total and not vat_total.startswith("€")
        else vat_total
    )
    tbl_data.append([
        Paragraph("<b>Общо (вкл. ДДС)</b>", s_bold),
        "", "", "",
        Paragraph(f"<b>{vat_display or '€ ___'}</b>", s_bold),
    ])

    tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        # Header
        ("BACKGROUND",    (0, 0),  (-1, 0),  BRAND_GREEN),
        ("TEXTCOLOR",     (0, 0),  (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0),  (-1, 0),  BOLD),
        ("FONTSIZE",      (0, 0),  (-1, 0),  9),
        ("LINEBELOW",     (0, 0),  (-1, 0),  1.0, BRAND_GOLD),
        # Data rows — alternating cream
        *[
            ("BACKGROUND", (0, i), (-1, i), BRAND_CREAM)
            for i in range(2, len(tbl_data) - 1, 2)
        ],
        # Totals row
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#E8F0EF")),
        ("LINEABOVE",     (0, -1), (-1, -1), 1.0, BRAND_GOLD),
        ("SPAN",          (0, -1), (3, -1)),
        # All cells
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
    services = data.get("additional_services", {})
    any_selected = False
    for key, label, price in service_defs:
        svc = services.get(key, {})
        if svc.get("selected"):
            any_selected = True
            note = svc.get("note", "").strip()
            note_part = f" — {note}" if note else ""
            story.append(Paragraph(
                f"<font color='#19514A'>✓</font>  <b>{label}</b>"
                f"  <font color='#888888'>({price})</font>{note_part}",
                s_body,
            ))
    if not any_selected:
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
    sig_data = [
        [
            Paragraph("Lozenets Lounge (Подпис и Дата)", s_sig),
            Paragraph("Клиент (Подпис и Дата)", s_sig),
        ],
        [
            Paragraph("____________________________", s_sig),
            Paragraph("____________________________", s_sig),
        ],
    ]
    sig_tbl = Table(sig_data, colWidths=[9 * cm, 9 * cm])
    sig_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_tbl)

    doc.build(story)


# ══════════════════════════════════════════════════════════════════════════
#  TKINTER UI — brand colours
# ══════════════════════════════════════════════════════════════════════════

BG           = "#F5F0E8"    # warm cream background
BRAND_G_HEX  = "#19514A"    # brand green (hex string for tkinter)
BRAND_GOLD_H = "#E9D281"    # gold
HEADER_TEXT  = "#FFFFFF"

FONT_UI      = ("Arial", 11)
FONT_UI_BOLD = ("Arial", 11, "bold")
FONT_HEADING = ("Arial", 13, "bold")
FONT_SMALL   = ("Arial",  9)


def section_label(parent, text):
    frm = tk.Frame(parent, bg=BRAND_G_HEX, pady=5)
    frm.pack(fill="x", pady=(14, 4))
    # Gold left accent bar
    tk.Frame(frm, bg=BRAND_GOLD_H, width=4).pack(side="left", fill="y")
    tk.Label(frm, text=text, font=FONT_HEADING, bg=BRAND_G_HEX, fg="white",
             padx=10).pack(side="left", anchor="w")


def field_row(parent, label, widget_factory, **kw):
    row = tk.Frame(parent, bg=BG)
    row.pack(fill="x", padx=16, pady=3)
    tk.Label(row, text=label, font=FONT_UI, bg=BG,
             width=28, anchor="w").pack(side="left")
    w = widget_factory(row, **kw)
    w.pack(side="left", fill="x", expand=True)
    return w


# ══════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════

class OfferApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lozenets Lounge — Генератор на Оферти")
        self.geometry("900x840")
        self.resizable(True, True)
        self.configure(bg=BG)
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Top bar ────────────────────────────────────────────────────────
        bar = tk.Frame(self, bg=BRAND_G_HEX, pady=0)
        bar.pack(fill="x")

        # Logo icon in header bar
        if os.path.exists(LOGO_ICON):
            try:
                from PIL import Image as PILImage, ImageTk
                img = PILImage.open(LOGO_ICON).resize((52, 52), PILImage.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(img)
                tk.Label(bar, image=self._logo_img, bg=BRAND_G_HEX,
                         pady=4, padx=10).pack(side="left")
            except Exception:
                pass

        text_bar = tk.Frame(bar, bg=BRAND_G_HEX)
        text_bar.pack(side="left", pady=8)
        tk.Label(text_bar, text="Lozenets Lounge",
                 font=("Arial", 17, "bold"), bg=BRAND_G_HEX,
                 fg="white").pack(anchor="w")
        tk.Label(text_bar, text="Оферта за клиент",
                 font=("Arial", 10), bg=BRAND_G_HEX,
                 fg=BRAND_GOLD_H).pack(anchor="w")

        # Gold accent strip
        tk.Frame(self, bg=BRAND_GOLD_H, height=3).pack(fill="x")

        # ── Scrollable canvas ───────────────────────────────────────────────
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.form_frame = tk.Frame(canvas, bg=BG)
        self._cwin = canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        self.form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(self._cwin, width=e.width),
        )
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * e.delta / 120), "units"))

        self._fill_form(self.form_frame)

        # ── Bottom button bar ───────────────────────────────────────────────
        btn_bar = tk.Frame(self, bg=BRAND_G_HEX, pady=10)
        btn_bar.pack(fill="x", side="bottom")
        tk.Frame(btn_bar, bg=BRAND_GOLD_H, height=2).pack(fill="x")
        tk.Button(
            btn_bar,
            text="⬇   Генерирай и запази PDF",
            font=("Arial", 12, "bold"),
            bg=BRAND_GOLD_H, fg=BRAND_G_HEX,
            activebackground="#dab55d",
            relief="flat", padx=24, pady=10,
            cursor="hand2",
            command=self._generate_pdf,
        ).pack(pady=8)

    def _fill_form(self, parent):
        # ── 1. Client ──────────────────────────────────────────────────────
        section_label(parent, "1.  Клиент")
        self.client_name = field_row(
            parent, "Уважаеми/а:", tk.Entry,
            font=FONT_UI, bg="white", relief="solid", bd=1,
        )

        # ── 2. Event description ───────────────────────────────────────────
        section_label(parent, "2.  Описание на събитие")
        desc_frame = tk.Frame(parent, bg=BG)
        desc_frame.pack(fill="x", padx=16, pady=3)
        tk.Label(desc_frame, text="Описание:", font=FONT_UI,
                 bg=BG, width=28, anchor="nw").pack(side="left", anchor="n")
        self.event_desc = tk.Text(
            desc_frame, font=FONT_UI, bg="white",
            height=5, wrap="word", relief="solid", bd=1,
        )
        self.event_desc.pack(side="left", fill="x", expand=True)

        # ── 2.1 Included items ─────────────────────────────────────────────
        section_label(parent, "2.1.  Какво е включено")
        items_frame = tk.Frame(parent, bg=BG)
        items_frame.pack(fill="x", padx=16, pady=3)
        tk.Label(items_frame, text="(един ред = една точка)",
                 font=FONT_SMALL, bg=BG, fg="grey").pack(anchor="w")
        self.included_text = tk.Text(
            items_frame, font=FONT_UI, bg="white",
            height=5, wrap="word", relief="solid", bd=1,
        )
        self.included_text.pack(fill="x")
        self.included_text.insert(
            "1.0", "Наем на пространството\nАудио оборудване\nКлиматизация"
        )

        # ── 3. Pricing ─────────────────────────────────────────────────────
        section_label(parent, "3.  Цена")
        self._build_pricing_table(parent)

        # ── 4. Additional services ─────────────────────────────────────────
        section_label(parent, "4.  Допълнителни Услуги")
        self._build_services(parent)

        # ── 6. Validity ────────────────────────────────────────────────────
        section_label(parent, "6.  Валидност на офертата")
        self.valid_until = field_row(
            parent, "Валидна до:", tk.Entry,
            font=FONT_UI, bg="white", relief="solid", bd=1,
        )
        self.valid_until.insert(0, date.today().strftime("%d.%m.%Y"))

        # ── Total ──────────────────────────────────────────────────────────
        section_label(parent, "Обща сума (вкл. ДДС)")
        self.total_vat = field_row(
            parent, "Общо €:", tk.Entry,
            font=FONT_UI, bg="white", relief="solid", bd=1,
        )
        tk.Label(
            parent,
            text="  Оставете празно за автоматично изчисление от ценовата таблица.",
            font=FONT_SMALL, bg=BG, fg="grey",
        ).pack(anchor="w", padx=16)

        tk.Frame(parent, bg=BG, height=24).pack()

    # ── Pricing table ──────────────────────────────────────────────────────
    def _build_pricing_table(self, parent):
        self._price_wrapper = tk.Frame(parent, bg=BG)
        self._price_wrapper.pack(fill="x", padx=16, pady=4)

        headers  = ["Описание", "Цена / час (€)", "Продължителност",
                    "Такси / Отстъпки / Други", "Общо (€)"]
        col_w    = [22, 14, 14, 22, 10]
        for col, (h, w) in enumerate(zip(headers, col_w)):
            tk.Label(
                self._price_wrapper, text=h,
                font=("Arial", 9, "bold"),
                bg=BRAND_G_HEX, fg="white",
                width=w, anchor="center", pady=5,
            ).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        self.price_row_entries = []
        self._price_row_count  = 0
        self._add_price_row("Почасово наемане", "75", "2 ч.", "", "150")

        btn_row = tk.Frame(parent, bg=BG)
        btn_row.pack(anchor="w", padx=16, pady=2)
        tk.Button(
            btn_row, text="+ Добави ред",
            font=FONT_SMALL, bg=BRAND_GOLD_H, fg=BRAND_G_HEX,
            relief="flat", padx=8, pady=3, cursor="hand2",
            command=lambda: self._add_price_row(),
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            btn_row, text="− Премахни последен ред",
            font=FONT_SMALL, bg="#ddd", fg="#333",
            relief="flat", padx=8, pady=3, cursor="hand2",
            command=self._remove_last_price_row,
        ).pack(side="left")

    def _add_price_row(self, desc="", pph="", dur="", fees="", total=""):
        row_idx  = self._price_row_count + 1
        defaults = [desc, pph, dur, fees, total]
        col_w    = [22, 14, 14, 22, 10]
        entries  = []
        for col, (val, w) in enumerate(zip(defaults, col_w)):
            bg = "#EFF5F4" if row_idx % 2 == 0 else "white"
            e = tk.Entry(
                self._price_wrapper, font=("Arial", 10),
                bg=bg, width=w, relief="solid", bd=1,
            )
            e.insert(0, val)
            e.grid(row=row_idx, column=col, sticky="nsew",
                   padx=1, pady=1, ipady=3)
            entries.append(e)
        self.price_row_entries.append(entries)
        self._price_row_count += 1

    def _remove_last_price_row(self):
        if not self.price_row_entries:
            return
        for e in self.price_row_entries.pop():
            e.destroy()
        self._price_row_count -= 1

    # ── Additional services ────────────────────────────────────────────────
    def _build_services(self, parent):
        self.service_vars  = {}
        self.service_notes = {}
        services = [
            ("bar",        "Бар и пакет с напитки",                          "цена при запитване"),
            ("catering",   "Кетъринг / бюфет",                               "цена при запитване"),
            ("flowers",    "Флорална декорация",                              "цена при запитване"),
            ("sound",      "Ъпгрейд на професионална озвучителна система",    "цена при запитване"),
            ("photo",      "Фотография / видеозаснемане",                     "цена при запитване"),
            ("extra_time", "Удължено време за подготовка",                    "€50 / час"),
        ]
        svc_frame = tk.Frame(parent, bg=BG)
        svc_frame.pack(fill="x", padx=16, pady=4)

        for key, label, price in services:
            var = tk.BooleanVar()
            self.service_vars[key] = var

            row = tk.Frame(svc_frame, bg=BG)
            row.pack(fill="x", pady=3)

            cb = tk.Checkbutton(
                row,
                text=f"{label}   ({price})",
                variable=var,
                font=FONT_UI,
                bg=BG, activebackground=BG,
                selectcolor=BRAND_G_HEX,
                fg="#333",
            )
            cb.pack(side="left")

            note_entry = tk.Entry(
                row, font=("Arial", 10), bg="white",
                width=26, relief="solid", bd=1, fg="grey",
            )
            note_entry.insert(0, "бележка (незадължително)")

            def _fi(e, ent=note_entry):
                if ent.get() == "бележка (незадължително)":
                    ent.delete(0, "end")
                    ent.config(fg="black")

            def _fo(e, ent=note_entry):
                if not ent.get().strip():
                    ent.insert(0, "бележка (незадължително)")
                    ent.config(fg="grey")

            note_entry.bind("<FocusIn>",  _fi)
            note_entry.bind("<FocusOut>", _fo)
            note_entry.pack(side="left", padx=10)
            self.service_notes[key] = note_entry

    # ── Data collection ────────────────────────────────────────────────────
    def _collect_data(self) -> dict:
        price_rows = []
        for entries in self.price_row_entries:
            vals = [e.get().strip() for e in entries]
            if any(vals):
                price_rows.append({
                    "description":    vals[0],
                    "price_per_hour": vals[1],
                    "duration":       vals[2],
                    "fees":           vals[3],
                    "total":          vals[4],
                })

        services = {}
        for key, var in self.service_vars.items():
            raw = self.service_notes[key].get().strip()
            note = "" if raw == "бележка (незадължително)" else raw
            services[key] = {"selected": var.get(), "note": note}

        included = [
            l.strip()
            for l in self.included_text.get("1.0", "end").strip().splitlines()
            if l.strip()
        ]

        return {
            "client_name":         self.client_name.get().strip(),
            "event_description":   self.event_desc.get("1.0", "end").strip(),
            "included_items":      included,
            "price_rows":          price_rows,
            "additional_services": services,
            "valid_until":         self.valid_until.get().strip(),
            "total_vat":           self.total_vat.get().strip(),
        }

    # ── PDF generation ─────────────────────────────────────────────────────
    def _generate_pdf(self):
        data        = self._collect_data()
        client_slug = data["client_name"].replace(" ", "_") or "Клиент"
        default     = f"Оферта_{client_slug}.pdf"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF файл", "*.pdf")],
            initialfile=default,
            title="Запази офертата като…",
        )
        if not filepath:
            return

        try:
            build_pdf(data, filepath)
            messagebox.showinfo(
                "Готово!",
                f"PDF офертата е запазена успешно:\n{filepath}",
            )
            import subprocess
            subprocess.Popen(["open", filepath])
        except Exception as exc:
            messagebox.showerror("Грешка", f"Неуспешно генериране на PDF:\n{exc}")


# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = OfferApp()
    app.mainloop()
