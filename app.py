#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lozenets Lounge — Оферта генератор
Run locally:  streamlit run app.py
"""

import base64
import io
import os
from datetime import date, timedelta

import streamlit as st

from pdf_builder import build_pdf

# ══════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Lozenets Lounge — Оферта",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_DIR       = os.path.dirname(os.path.abspath(__file__))
LOGO_ICON  = os.path.join(_DIR, "logo_icon.png")
LOGO_HOUSE = os.path.join(_DIR, "logo_house.png")

GREEN  = "#19514A"
GOLD   = "#E9D281"
CREAM  = "#F5F0E8"


# ══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════
def img_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def section(title: str):
    st.markdown(
        f"""<div style="
            background:{GREEN}; color:white; font-weight:700;
            font-size:1rem; padding:8px 16px; margin-top:22px;
            margin-bottom:6px; border-left:5px solid {GOLD};
            border-radius:2px;">
            {title}
        </div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
  /* Page background */
  .stApp {{ background-color: {CREAM}; }}

  /* Hide Streamlit top bar colour */
  header[data-testid="stHeader"] {{ background: {GREEN}; }}

  /* Input fields */
  div[data-testid="stTextInput"] input,
  div[data-testid="stTextArea"] textarea {{
      background: white !important;
  }}

  /* Number input */
  div[data-testid="stNumberInput"] input {{
      background: white !important;
  }}

  /* Primary button */
  div[data-testid="stButton"] button[kind="primary"] {{
      background-color: {GREEN} !important;
      color: white !important;
      font-weight: 700 !important;
      border: none !important;
  }}

  /* Download button */
  div[data-testid="stDownloadButton"] > button {{
      background-color: {GOLD} !important;
      color: {GREEN} !important;
      font-weight: 700 !important;
      font-size: 1.05rem !important;
      border: none !important;
      width: 100%;
      padding: 0.55rem 1rem !important;
  }}

  /* Remove excess top padding */
  .block-container {{ padding-top: 0 !important; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  TOP BANNER
# ══════════════════════════════════════════════════════════════════════════
if os.path.exists(LOGO_ICON):
    b64 = img_b64(LOGO_ICON)
    st.markdown(f"""
    <div style="background:{GREEN}; padding:12px 24px; display:flex;
                align-items:center; gap:18px;
                border-bottom:4px solid {GOLD}; margin-bottom:4px;">
      <img src="data:image/png;base64,{b64}"
           style="height:60px; width:60px; object-fit:contain;"/>
      <div>
        <div style="color:white; font-size:1.55rem; font-weight:700;
                    line-height:1.2;">Lozenets Lounge</div>
        <div style="color:{GOLD}; font-size:0.88rem; margin-top:2px;">
            Генератор на Оферти
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background:{GREEN}; padding:14px 24px;
                border-bottom:4px solid {GOLD}; margin-bottom:4px;">
      <span style="color:white; font-size:1.55rem; font-weight:700;">
          Lozenets Lounge
      </span>
      <span style="color:{GOLD}; font-size:0.88rem; margin-left:14px;">
          Генератор на Оферти
      </span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  SESSION STATE  — pricing rows
#  Each row: description (str), price_per_hour (float),
#            duration (float hours), fees (float, negative = discount)
# ══════════════════════════════════════════════════════════════════════════
if "rows" not in st.session_state:
    st.session_state.rows = [
        {"description": "Почасово наемане", "price_per_hour": 75.0,
         "duration": 2.0, "discount": 0.0}
    ]


def _add_row():
    st.session_state.rows.append(
        {"description": "", "price_per_hour": 0.0, "duration": 0.0, "discount": 0.0}
    )


def _del_row():
    if len(st.session_state.rows) > 1:
        st.session_state.rows.pop()


# ══════════════════════════════════════════════════════════════════════════
#  LAYOUT  — two columns
# ══════════════════════════════════════════════════════════════════════════
col_form, col_info = st.columns([3, 1], gap="large")

# ─────────────────────────────────────────────────────────────────────────
with col_form:

    # ── 1. Client ──────────────────────────────────────────────────────────
    section("1.  Клиент")
    client_name = st.text_input(
        "Уважаеми/а:",
        placeholder="Иван Петров / Фирма ООД",
        key="client_name",
    )

    # ── 2. Event description ───────────────────────────────────────────────
    section("2.  Описание на събитие")
    event_description = st.text_area(
        "Описание:",
        placeholder="Например: Корпоративно събитие за 30 човека, петък 20 юни 2025, 18:00–22:00",
        height=100,
        key="event_desc",
    )

    # ── 2.1 Included items ─────────────────────────────────────────────────
    section("2.1.  Какво е включено")
    st.caption("Всеки ред = отделна точка в PDF-а.")
    included_raw = st.text_area(
        "included",
        value="Наем на пространството\nАудио оборудване\nКлиматизация",
        height=110,
        label_visibility="collapsed",
        key="included",
    )

    # ── 3. Pricing ─────────────────────────────────────────────────────────
    section("3.  Цена")
    st.caption("Общото за всеки ред и ДДС 20% се изчисляват автоматично.")

    # Table column headers
    hc = st.columns([3, 2, 2, 2, 2])
    for col, lbl in zip(hc, ["Описание", "Цена / час (€)",
                               "Часове", "Отстъпка (%)", "Общо (€)"]):
        col.markdown(
            f"<div style='background:{GREEN}; color:white; font-weight:700;"
            f"font-size:0.82rem; padding:5px 6px; text-align:center;"
            f"border-radius:2px;'>{lbl}</div>",
            unsafe_allow_html=True,
        )

    # Data rows
    for i, row in enumerate(st.session_state.rows):
        c0, c1, c2, c3, c4 = st.columns([3, 2, 2, 2, 2])

        row["description"] = c0.text_input(
            "desc", value=row["description"],
            key=f"desc_{i}", label_visibility="collapsed",
            placeholder="Описание на услугата",
        )
        row["price_per_hour"] = c1.number_input(
            "price", value=float(row["price_per_hour"]),
            min_value=0.0, step=5.0, format="%.2f",
            key=f"price_{i}", label_visibility="collapsed",
        )
        row["duration"] = c2.number_input(
            "hours", value=float(row["duration"]),
            min_value=0.0, step=0.5, format="%.1f",
            key=f"dur_{i}", label_visibility="collapsed",
        )
        row["discount"] = c3.number_input(
            "disc", value=float(row.get("discount", 0.0)),
            min_value=0.0, max_value=100.0, step=1.0, format="%.0f",
            key=f"disc_{i}", label_visibility="collapsed",
            help="Въведете % отстъпка (0–100)",
        )
        row_total = row["price_per_hour"] * row["duration"] * (1 - row["discount"] / 100)
        c4.markdown(
            f"<div style='background:#EAF1F0; border:1px solid #ccc;"
            f"border-radius:4px; padding:7px 8px; font-weight:700;"
            f"text-align:center; margin-top:1px;'>"
            f"€ {row_total:,.2f}</div>",
            unsafe_allow_html=True,
        )

    # Add / remove row buttons
    ba, br, _ = st.columns([1.3, 2.0, 4.0])
    ba.button("＋ Добави ред",            on_click=_add_row, key="add_row")
    br.button("－ Премахни последен ред", on_click=_del_row, key="del_row",
              disabled=len(st.session_state.rows) <= 1)

    # Live totals summary
    total = sum(r["price_per_hour"] * r["duration"] * (1 - r.get("discount", 0.0) / 100)
                for r in st.session_state.rows)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    _, tc = st.columns([4, 2])
    tc.markdown(
        f"<div style='text-align:center; background:{GREEN}; color:white;"
        f"border-radius:6px; padding:8px 10px; font-size:0.95rem;'>"
        f"Обща цена:<br/><b style='font-size:1.15rem;'>€ {total:,.2f}</b></div>",
        unsafe_allow_html=True,
    )

    # ── 4. Additional services ─────────────────────────────────────────────
    section("4.  Допълнителни Услуги")

    SERVICE_DEFS = [
        ("bar",        "Бар и пакет с напитки",       "цена при запитване"),
        ("catering",   "Кетъринг / бюфет",            "цена при запитване"),
        ("flowers",    "Флорална декорация",           "цена при запитване"),
        ("photo",      "Фотография / видеозаснемане",  "цена и наличност при запитване"),
        ("extra_time", "Удължено време за подготовка", "€50 / час"),
    ]

    services = {}
    for key, label, price in SERVICE_DEFS:
        ca, cb = st.columns([2, 3])
        selected = ca.checkbox(
            f"{label}  —  *{price}*", key=f"svc_{key}"
        )
        note = (
            cb.text_input(
                "note", placeholder="бележка (незадължително)",
                key=f"note_{key}", label_visibility="collapsed",
            )
            if selected else ""
        )
        services[key] = {"selected": selected, "note": note}

    # ── 6. Validity ────────────────────────────────────────────────────────
    section("6.  Валидност на офертата")
    valid_date = st.date_input(
        "Офертата е валидна до:",
        value=date.today() + timedelta(days=14),
        format="DD.MM.YYYY",
        key="valid_date",
    )
    valid_str = valid_date.strftime("%d.%m.%Y")

    # ── Generate & Download ────────────────────────────────────────────────
    st.markdown("<hr style='border-color:#ccc; margin-top:24px;'/>",
                unsafe_allow_html=True)

    if st.button("📄  Генерирай PDF оферта",
                 type="primary", use_container_width=True):

        pdf_rows = [
            {
                "description":    r["description"],
                "price_per_hour": f"€ {r['price_per_hour']:,.2f} / час",
                "duration":       f"{r['duration']:.1f} ч.",
                "fees":           (f"{r['discount']:.0f}%" if r.get("discount", 0) else "—"),
                "total":          f"€ {r['price_per_hour'] * r['duration'] * (1 - r.get('discount', 0) / 100):,.2f}",
            }
            for r in st.session_state.rows
        ]

        data = {
            "client_name":         client_name,
            "event_description":   event_description,
            "included_items":      [l.strip() for l in included_raw.splitlines()
                                    if l.strip()],
            "price_rows":          pdf_rows,
            "additional_services": services,
            "valid_until":         valid_str,
            "total_vat_str":       f"€ {total:,.2f}",
        }

        buf = io.BytesIO()
        try:
            build_pdf(data, buf)
            buf.seek(0)
            st.session_state["pdf_bytes"]  = buf.getvalue()
            st.session_state["pdf_client"] = (
                client_name.strip().replace(" ", "_") or "Клиент"
            )
            st.success("✅  PDF е готов — натиснете бутона по-долу за изтегляне.")
        except Exception as exc:
            st.error(f"Грешка при генериране на PDF: {exc}")

    if "pdf_bytes" in st.session_state:
        st.download_button(
            label="⬇  Изтегли PDF офертата",
            data=st.session_state["pdf_bytes"],
            file_name=f"Оферта_{st.session_state['pdf_client']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────
with col_info:
    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

    # Logo card
    logo_path = LOGO_ICON if os.path.exists(LOGO_ICON) else (
                LOGO_HOUSE if os.path.exists(LOGO_HOUSE) else None)
    if logo_path:
        b64l = img_b64(logo_path)
        st.markdown(f"""
        <div style="text-align:center; background:{GREEN}; padding:20px 14px;
                    border-radius:8px; border:2px solid {GOLD};">
          <img src="data:image/png;base64,{b64l}"
               style="width:110px; height:110px; object-fit:contain;"/>
          <div style="color:{GOLD}; font-size:1rem; font-weight:700;
                      margin-top:10px;">Lozenets Lounge</div>
          <div style="color:white; font-size:0.78rem; margin-top:3px;">
              est. 1942
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Tips card
    st.markdown(f"""
    <div style="background:white; border-left:4px solid {GOLD};
                padding:14px 14px; border-radius:4px; font-size:0.83rem;
                line-height:1.6;">
      <b>Съвети</b><br/><br/>
      ● <b>Общо</b> = Цена × Часове × (1 − Отстъпка %)<br/>
      ● Въведете 10 в <i>Отстъпка</i> за 10% намаление<br/>
      ● <b>ДДС 20%</b> и крайната сума са автоматични<br/>
      ● Всеки ред в <i>Включено</i> = отделна точка в PDF<br/>
      ● Датата за валидност се избира с календара
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Contact card
    st.markdown(f"""
    <div style="background:{GREEN}; color:white; padding:14px;
                border-radius:6px; font-size:0.8rem; text-align:center;
                line-height:1.7;">
      📍 София, Лозенец<br/>
      ул. Кръстьо Сарафов 22<br/>
      <span style="color:{GOLD};">@lozenets_lounge</span><br/>
      lozenetslounge.eu
    </div>
    """, unsafe_allow_html=True)
