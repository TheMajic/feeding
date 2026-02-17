from __future__ import annotations

import sys
from pathlib import Path
from io import BytesIO

import streamlit as st

# ================== PATH SETUP ==================
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ================== IMPORT CORE ==================
from feeding_ai.core import generate_from_text  # noqa: E402
from feeding_ai.lang import detect_lang  # noqa: E402

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Feeding AI - Sport Nutrition & Workouts",
    layout="centered",
)

st.title("Feeding AI")

# ================== LANGUAGE SELECT ==================
lang_choice = st.radio(
    "Language / اللغة",
    ["English", "العربية"],
    horizontal=True
)

is_ar = lang_choice == "العربية"

# ================== USER INPUTS ==================
st.subheader("بياناتك" if is_ar else "Your Information")

col1, col2 = st.columns(2)

with col1:
    height = st.number_input(
        "الطول (سم)" if is_ar else "Height (cm)",
        min_value=50,
        max_value=250,
        step=1,
        format="%d",
    )

with col2:
    weight = st.number_input(
        "الوزن (كجم)" if is_ar else "Weight (kg)",
        min_value=20,
        max_value=250,
        step=1,
        format="%d",
    )

sports_list = [
    "Running", "Swimming", "Cycling", "Gym / Bodybuilding",
    "Boxing", "Tennis", "Martial Arts", "Yoga", "CrossFit",
    "Football", "Basketball", "Volleyball", "Handball",
    "Hockey", "Rugby"
]

sport = st.selectbox(
    "الرياضة" if is_ar else "Sport",
    sports_list
)

# ================== LLM OPTION ==================
use_llm = st.checkbox(
    "استخدام LLM (GPU / Transformers)" if is_ar else "Use LLM (GPU / Transformers)",
    value=False,
)

llm_model = None
if use_llm:
    llm_model = st.text_input(
        "HuggingFace Model (e.g. mistralai/Mistral-7B-Instruct-v0.3)",
        value="",
    ).strip() or None

# ================== GENERATE BUTTON ==================
if st.button("توليد الخطة" if is_ar else "Generate Plan"):

    if height == 0 or weight == 0:
        st.warning("من فضلك أدخل الطول والوزن." if is_ar else "Please enter height and weight.")
    else:
        with st.spinner("جارٍ التوليد..." if is_ar else "Generating..."):
            try:
                if is_ar:
                    user_text = f"طولي {height} سم ووزني {weight} كجم وأمارس {sport}"
                else:
                    user_text = f"I am {height} cm, {weight} kg, I play {sport}"

                res = generate_from_text(user_text, llm_base_model=llm_model)

                st.subheader("الخطة المولدة" if is_ar else "Generated Plan")
                st.markdown(res.text)

                # حفظ النص
                st.session_state["generated_plan"] = res.text

            except Exception as e:
                st.error(str(e))

# ================== PDF DOWNLOAD ==================
if "generated_plan" in st.session_state:

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # -------- FONT PATH --------
    font_path = ROOT / "feeding_ai" / "assets" / "fonts" / "Amiri-Regular.ttf"
    pdfmetrics.registerFont(TTFont("CustomArabic", str(font_path)))

    generated_text = st.session_state["generated_plan"]

    # كشف عربي تلقائي
    is_arabic_output = any("\u0600" <= c <= "\u06FF" for c in generated_text)
    alignment = TA_RIGHT if is_arabic_output else TA_LEFT

    style = ParagraphStyle(
        name="CustomStyle",
        fontName="CustomArabic",
        fontSize=12,
        leading=18,
        alignment=alignment,
    )

    # نحافظ على تنسيق الأسطر
    formatted_text = generated_text.replace("\n", "<br/>")

    elements.append(Paragraph(formatted_text, style))
    elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)

    st.download_button(
        label="تحميل كـ PDF" if is_ar else "Download as PDF",
        data=buffer.getvalue(),
        file_name="feeding_ai_plan.pdf",
        mime="application/pdf"
    )
