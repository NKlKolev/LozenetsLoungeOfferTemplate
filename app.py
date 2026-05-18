#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lozenets Lounge — Streamlit offer generator.
Run with:  streamlit run app.py
"""

import io
import os
import base64
from datetime import date, timedelta

import streamlit as st
from pdf_builder import build_pdf

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lozenets Lounge — Оферта",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Brand colours (CSS) ────────────────────────────────────────────────────
BRAND_GREEN = "#19514A"
BRAND_GOLD  = "#E9D281"
BRAND_CREAM = "#F5F0E8"

# ── Inject CSS ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* Overall background */
  .stApp {{ background-color: {BRAND_CREAM}; }}

  /* Hide default Streamlit header chrome */
  header[data-testid="stHeader"] {{ background-color: {BRAND_GREEN}; }}

  /* Section titles */
  .section-header {{
      background-color: {BRAND_GREEN};
      color: white;
      padding: 8px 16px;
      border-left: 5px solid {BRAND_GOLD};
      border-radius: 2px;
      font-size: 1rem;
      font-weight: 700;
      margin-top: 24px;
      margin-bottom: 8px;
  }}

  /* Download button */
  div[data-testid="stDownloadButton"] button {{
      background-color: {BRAND_GOLD} !important;
      color: {BRAND_GREEN} !important;
      font-weight: 700 !important;
      font-size: 1.05rem !important;
      border: none !important;
      padding: 0.6rem 2rem !important;
      border-radius: 4px !important;
      width: 100%;
  }}
  div[data-testid="stDownloadButton"] button:hover {{
      background-color: #dab55d !important;
  }}

  /* Text inputs */
  input[type="text"], textarea {{
      background-color: white !important;
      border: 1px solid #ccc !important;
  }}

  /* Divider */
  hr {{ border-color: {BRAND_GOLD}; }}

  /* Remove top padding from main block */
  .block-container {{ padding-top: 0rem !important; }}
</style>
""", unsafe_allow_html=True)


# ── Logo helper ────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))

def _img_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

LOGO_ICON  = os.path.join(_HERE, "logo_icon.png")
LOGO_HOUSE = os.path.join(_HERE, "logo_house.png")

# ── Top banner ─────────────────────────────────────────────────────────────
if os.path.exists(LOGO_ICON):
    b64 = _img_b64(LOGO_ICON)
    st.markdown(f"""
    <div style="
        background:{BRAND_GREEN};
        padding:14px 28px;
        display:flex;
        align-items:center;
        gap:20px;
        border-bottom: 3px solid {BRAND_GOLD};
    ">
      <img src="data:image/png;base64,{b64}" style="height:64px; width:64px; object-fit:contain;" />
      <div>
        <div style="color:white; font-size:1.6rem; font-weight:700; line-height:1.2;">
            Lozenets Lounge
        </div>
        <div style="color:{BRAND_GOLD}; font-size:0.9rem;">
            Генератор на Оферти
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background:{BRAND_GREEN}; padding:18px 28px;
                border-bottom:3px solid {BRAND_GOLD};">
      <span style="color:white; font-size:1.6rem; font-weight:700;">Lozenets Lounge</span>
      <span style="color:{BRAND_GOLD}; font-size:0.9rem; margin-left:12px;">
        Генератор на Оферти
      </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  SESSION STATE — dynamic pricing rows
# ══════════════════════════════════════════════════════════════════════════
if "price_rows" not in st.session_state:
    st.session_state.price_rows = [
        {"description": "Почасово наемане", "price_per_hour": "€ 75 / час",
         "duration": "2 ч.", "fees": "", "total": "150"},
    ]


def add_row():
    st.session_state.price_rows.append(
        {"description": "", "price_per_hour": "", "duration": "", "fees": "", "total": ""}
    )


def remove_row():
    if len(st.session_state.price_rows) > 1:
        st.session_state.price_rows.pop()


# ── Section label helper ───────────────────────────────────────────────────
def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  FORM
# ══════════════════════════════════════════════════════════════════════════
left, right = st.columns([3, 1])

with left:

    # ── 1. Client ──────────────────────────────────────────────────────────
    section("1.  Клиент")
    client_name = st.text_input(
        "Уважаеми/а:", placeholder="Иван Петров / Фирма ООД"
    )

    # ── 2. Event description ───────────────────────────────────────────────
    section("2.  Описание на събитие")
    event_description = st.text_area(
        "Описание на събитието:",
        placeholder="Например: Корпоративно събитие за 30 човека, петък 20 юни 2025, 18:00–22:00",
        height=100,
    )

    # ── 2.1 Included items ─────────────────────────────────────────────────
    section("2.1.  Какво е включено")
    st.caption("Въведете всяко включено нещо на отделен ред.")
    included_raw = st.text_area(
        "Включено:",
        value="Наем на пространството\nАудио оборудване\nКлиматизация",
        height=110,
        label_visibility="collapsed",
    )

    # ── 3. Pricing ─────────────────────────────────────────────────────────
    section("3.  Цена")

    # Column headers
    h_cols = st.columns([3, 2, 2, 3, 2])
    headers = ["Описание", "Цена / час", "Продължителност",
               "Такси / Отстъпки / Други", "Общо (€)"]
    for col, header in zip(h_cols, headers):
        col.markdown(
            f"<div style='background:{BRAND_GREEN};color:white;"
            f"padding:4px 6px;font-weight:700;font-size:0.85rem;"
            f"text-align:center;border-radius:2px;'>{header}</div>",
            unsafe_allow_html=True,
        )

    # Editable price rows
    for i, row in enumerate(st.session_state.price_rows):
        cols = st.columns([3, 2, 2, 3, 2])
        row["description"]    = cols[0].text_input("Описание",          row["description"],    key=f"d_{i}", label_visibility="collapsed")
        row["price_per_hour"] = cols[1].text_input("Цена/час",          row["price_per_hour"], key=f"p_{i}", label_visibility="collapsed")
        row["duration"]       = cols[2].text_input("Продължителност",   row["duration"],       key=f"u_{i}", label_visibility="collapsed")
        row["fees"]           = cols[3].text_input("Такси/Отстъпки",    row["fees"],           key=f"f_{i}", label_visibility="collapsed")
        row["total"]          = cols[4].text_input("Общо",              row["total"],          key=f"t_{i}", label_visibility="collapsed")

    btn_c1, btn_c2, _ = st.columns([1.2, 2, 4])
    btn_c1.button("＋ Добави ред",           on_click=add_row)
    btn_c2.button("－ Премахни последен ред", on_click=remove_row,
                  disabled=len(st.session_state.price_rows) <= 1)

    total_vat = st.text_input(
        "Общо (вкл. ДДС) €:",
        placeholder="Оставете празно за автоматично изчисление",
    )

    # ── 4. Additional services ─────────────────────────────────────────────
    section("4.  Допълнителни Услуги")

    service_defs = [
        ("bar",        "Бар и пакет с напитки",                      "цена при запитване"),
        ("catering",   "Кетъринг / бюфет",                           "цена при запитване"),
        ("flowers",    "Флорална декорация",                          "цена при запитване"),
        ("sound",      "Ъпгрейд на професионална озвучителна система","цена при запитване"),
        ("photo",      "Фотография / видеозаснемане",                 "цена при запитване"),
        ("extra_time", "Удължено време за подготовка",                "€50 / час"),
    ]

    services = {}
    for key, label, price in service_defs:
        c1, c2 = st.columns([2, 3])
        selected = c1.checkbox(f"{label}  —  *{price}*", key=f"svc_{key}")
        note     = c2.text_input(
            "Бележка", placeholder="бележка (незадължително)",
            key=f"note_{key}", label_visibility="collapsed",
        ) if selected else ""
        services[key] = {"selected": selected, "note": note}

    # ── 6. Validity ────────────────────────────────────────────────────────
    section("6.  Валидност на офертата")
    valid_until_date = st.date_input(
        "Офертата е валидна до:",
        value=date.today() + timedelta(days=14),
        min_value=date.today(),
        format="DD.MM.YYYY",
    )
    valid_until_str = valid_until_date.strftime("%d.%m.%Y")

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── Generate PDF button ────────────────────────────────────────────────
    if st.button("📄  Генерирай PDF оферта", type="primary", use_container_width=True):
        data = {
            "client_name":         client_name,
            "event_description":   event_description,
            "included_items":      [l.strip() for l in included_raw.splitlines() if l.strip()],
            "price_rows":          list(st.session_state.price_rows),
            "additional_services": services,
            "valid_until":         valid_until_str,
            "total_vat":           total_vat,
        }
        buf = io.BytesIO()
        try:
            build_pdf(data, buf)
            buf.seek(0)
            st.session_state["pdf_bytes"]  = buf.getvalue()
            st.session_state["pdf_client"] = client_name.replace(" ", "_") or "Клиент"
            st.success("PDF е готов! Натиснете бутона по-долу за изтегляне.")
        except Exception as exc:
            st.error(f"Грешка при генериране на PDF: {exc}")

    if "pdf_bytes" in st.session_state:
        fname = f"Оферта_{st.session_state['pdf_client']}.pdf"
        st.download_button(
            label="⬇  Изтегли PDF офертата",
            data=st.session_state["pdf_bytes"],
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
        )


# ── Right column — tips ────────────────────────────────────────────────────
with right:
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

    if os.path.exists(LOGO_HOUSE):
        b64h = _img_b64(LOGO_HOUSE)
        st.markdown(f"""
        <div style="text-align:center; background:{BRAND_GREEN};
                    padding:20px; border-radius:8px;
                    border:2px solid {BRAND_GOLD};">
          <img src="data:image/png;base64,{b64h}"
               style="width:120px; height:120px; object-fit:contain;" />
          <div style="color:{BRAND_GOLD}; font-size:1.1rem;
                      font-weight:700; margin-top:10px;">
              Lozenets Lounge
          </div>
          <div style="color:white; font-size:0.8rem; margin-top:4px;">
              est. 1942
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:white; border-left:4px solid {BRAND_GOLD};
                padding:14px 16px; border-radius:4px; font-size:0.85rem;">
      <b>Съвети:</b><br/><br/>
      ● Полето <b>Общо (€)</b> се изчислява автоматично от редовете,
        ако го оставите празно.<br/><br/>
      ● Под <i>Какво е включено</i> — всеки ред е отделна точка в PDF-а.<br/><br/>
      ● Датата за валидност се избира с календара.<br/><br/>
      ● Можете да добавяте неограничен брой ценови редове.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{BRAND_GREEN}; color:white; padding:12px 16px;
                border-radius:4px; font-size:0.8rem; text-align:center;">
      📍 София, Лозенец<br/>
      ул. Кръстьо Сарафов 22<br/><br/>
      <span style="color:{BRAND_GOLD}">@lozenets_lounge</span><br/>
      lozenetslounge.eu
    </div>
    """, unsafe_allow_html=True)
