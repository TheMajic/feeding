from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure project root is importable when running via `streamlit run`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from feeding_ai.core import generate_from_text  # noqa: E402
from feeding_ai.lang import detect_lang  # noqa: E402

st.set_page_config(
    page_title="Feeding AI - Sport Nutrition & Workouts",
    layout="centered",
)

st.title("Feeding AI")
st.markdown("")

default_example_ar = "الطول ... سم الوزن ... كجم و رياضتي"
default_example_en = "I am ... cm, ... kg, I play ..."

with st.expander("Input examples"):
    st.code(default_example_ar, language="text")
    st.code(default_example_en, language="text")

user_text = st.text_area(
    "اكتب وصفك هنا (الطول + الوزن + الرياضة)",
)

use_llm = st.checkbox(
    "LLM (GPU / Transformers / Torch)",
    value=False,
)

llm_model = None
if use_llm:
    llm_model = st.text_input(
        "HuggingFace (mistralai/Mistral-7B-Instruct-v0.3)",
        value="",
        help="لو تركته فارغًا سيتم استخدام المولّد القائم على القواعد (Rule-based).",
    ).strip() or None


if st.button("Generate plan"):
    if not user_text.strip():
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Generating..."):
            try:
                res = generate_from_text(user_text, llm_base_model=llm_model)
                # لغة النتيجة
                lang = res.lang.code
                if lang == "ar":
                    st.subheader("الخطة المولّدة")
                else:
                    st.subheader("Generated plan")
                st.markdown(res.text)
            except Exception as e:
                # حاول نخلي رسالة الخطأ بنفس لغة الإدخال
                lang = detect_lang(user_text).code
                msg = str(e)
                if lang == "ar":
                    st.error(f"حدث خطأ أثناء التوليد: {msg}")
                else:
                    st.error(f"Error while generating plan: {msg}")