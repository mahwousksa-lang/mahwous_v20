import streamlit as st
import pandas as pd
import json
import requests
from engines.engine import run_full_analysis
from engines.hybrid_matcher import hybrid_score
from engines.ai_engine import ai_chat, ai_market_lookup, ai_product_description
from utils.helpers import normalize_text
from utils.make_helper import send_to_make
from config import Config
from styles import MAIN_CSS

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="MahwousStore v22",
    layout="wide",
)

st.markdown(MAIN_CSS, unsafe_allow_html=True)

st.title("🧪 MahwousStore v22 — نظام التسعير الذكي + المطابقة المتقدمة")
st.write("نسخة كاملة نظيفة تشمل كل ميزات v19 + محرك المطابقة الجديد Hybrid Arabic‑BERT")

# ---------------------------------------------------------
# الشريط الجانبي
# ---------------------------------------------------------
st.sidebar.header("📂 رفع الملفات")

file_my = st.sidebar.file_uploader("ملف مهووس (CSV/Excel)", type=["csv", "xlsx"])
files_competitors = st.sidebar.file_uploader(
    "ملفات المنافسين (1–5 ملفات)", type=["csv", "xlsx"], accept_multiple_files=True
)

start_button = st.sidebar.button("🚀 بدء التحليل")

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 لوحة التحكم",
    "🔵 المنتجات المفقودة",
    "🔍 مقارنة منتجين",
    "💹 بحث سوق",
    "🤖 الذكاء الاصطناعي"
])

# ---------------------------------------------------------
# 1) لوحة التحكم
# ---------------------------------------------------------
with tab1:
    st.subheader("📊 لوحة التحكم")

    if start_button and file_my and files_competitors:
        st.info("جاري التحليل…")

        df_my = pd.read_csv(file_my) if file_my.name.endswith(".csv") else pd.read_excel(file_my)

        dfs_comp = []
        for f in files_competitors:
            df = pd.read_csv(f) if f.name.endswith(".csv") else pd.read_excel(f)
            dfs_comp.append(df)

        results = run_full_analysis(df_my, dfs_comp)

        st.success("تم التحليل بنجاح!")

        st.write("### 🔴 سعر أعلى")
        st.dataframe(results["higher"], use_container_width=True)

        st.write("### 🟢 سعر أقل")
        st.dataframe(results["lower"], use_container_width=True)

        st.write("### ✅ موافق عليها")
        st.dataframe(results["approved"], use_container_width=True)

        st.write("### 🔵 مفقودة")
        st.dataframe(results["missing"], use_container_width=True)

    else:
        st.warning("يرجى رفع الملفات ثم الضغط على زر التحليل.")

# ---------------------------------------------------------
# 2) المنتجات المفقودة
# ---------------------------------------------------------
with tab2:
    st.subheader("🔵 المنتجات المفقودة — محرك Hybrid Arabic‑BERT")

    file_my2 = st.file_uploader("ملف منتجاتك", type=["csv", "xlsx"], key="my2")
    file_comp2 = st.file_uploader("ملف المنافس", type=["csv", "xlsx"], key="comp2")

    if file_my2 and file_comp2:
        df_my = pd.read_csv(file_my2) if file_my2.name.endswith(".csv") else pd.read_excel(file_my2)
        df_comp = pd.read_csv(file_comp2) if file_comp2.name.endswith(".csv") else pd.read_excel(file_comp2)

        results = []

        with st.spinner("جاري المطابقة…"):
            for _, row_c in df_comp.iterrows():
                best_match = None
                best_score = 0

                for _, row_m in df_my.iterrows():
                    score = hybrid_score(str(row_c["name"]), str(row_m["name"]))
                    if score > best_score:
                        best_score = score
                        best_match = row_m["name"]

                status = (
                    "مطابق" if best_score >= 0.90 else
                    "موجود باسم مختلف" if best_score >= 0.75 else
                    "مراجعة" if best_score >= 0.55 else
                    "مفقود فعليًا"
                )

                results.append({
                    "منتج المنافس": row_c["name"],
                    "أفضل تطابق": best_match,
                    "النتيجة": round(best_score, 3),
                    "الحالة": status
                })

        df_res = pd.DataFrame(results)
        st.dataframe(df_res, use_container_width=True)

        st.download_button(
            "📥 تحميل النتائج CSV",
            df_res.to_csv(index=False).encode("utf-8-sig"),
            "missing_products.csv",
            "text/csv"
        )

# ---------------------------------------------------------
# 3) مقارنة منتجين
# ---------------------------------------------------------
with tab3:
    st.subheader("🔍 مقارنة منتجين")

    p1 = st.text_input("اسم المنتج الأول")
    p2 = st.text_input("اسم المنتج الثاني")

    if st.button("تحقق الآن"):
        score = hybrid_score(p1, p2)
        st.write("### النتيجة:", round(score, 3))

        if score >= 0.90:
            st.success("مطابق بنسبة عالية")
        elif score >= 0.75:
            st.info("موجود باسم مختلف")
        elif score >= 0.55:
            st.warning("يحتاج مراجعة")
        else:
            st.error("غير مطابق")

# ---------------------------------------------------------
# 4) بحث سوق
# ---------------------------------------------------------
with tab4:
    st.subheader("💹 بحث سوق")

    product_name = st.text_input("اسم المنتج للبحث")
    if st.button("ابحث"):
        result = ai_market_lookup(product_name)
        st.write(result)

# ---------------------------------------------------------
# 5) الذكاء الاصطناعي
# ---------------------------------------------------------
with tab5:
    st.subheader("🤖 الذكاء الاصطناعي")

    user_msg = st.text_area("اكتب سؤالك")
    if st.button("إرسال"):
        reply = ai_chat(user_msg)
        st.write(reply)
