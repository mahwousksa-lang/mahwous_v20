import streamlit as st
import pandas as pd
import time
import json

from utils.helpers import read_uploaded_file, extract_products, generate_session_id
from utils.make_helper import send_price_updates, send_missing_products, send_full_report
from engines.smart_engine import run_full_analysis, SmartEngineV21
from engines.ai_engine import AIEngine
from database.db_manager import DatabaseManager
from ui.styles import inject_css, render_header, render_stats_cards, render_product_card

from config import (
    WEBHOOK_UPDATE_PRICES,
    WEBHOOK_NEW_PRODUCTS,
    WEBHOOK_REPORT,
)


# ─────────────────────────────────────────────
# تهيئة الصفحة
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="مهووس v22 — نظام التسعير الذكي",
    page_icon="🧪",
    layout="wide"
)

inject_css()


# ─────────────────────────────────────────────
# تحميل قاعدة البيانات
# ─────────────────────────────────────────────
db = DatabaseManager()


# ─────────────────────────────────────────────
# إعدادات AI
# ─────────────────────────────────────────────
st.sidebar.title("⚙️ الإعدادات")

api_keys_raw = st.sidebar.text_area(
    "🔑 مفاتيح Gemini (كل مفتاح في سطر)",
    placeholder="AIzaSyA...."
)

api_keys = [k.strip() for k in api_keys_raw.split("\n") if k.strip()]
ai_engine = AIEngine(api_keys) if api_keys else None


# ─────────────────────────────────────────────
# رفع الملفات
# ─────────────────────────────────────────────
st.sidebar.subheader("📤 رفع الملفات")

my_file = st.sidebar.file_uploader("ملف منتجاتك", type=["csv", "xlsx"])
comp_files = st.sidebar.file_uploader(
    "ملفات المنافسين",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

start_btn = st.sidebar.button("🚀 بدء التحليل")


# ─────────────────────────────────────────────
# الواجهة الرئيسية
# ─────────────────────────────────────────────
render_header(
    ai_available=ai_engine.available if ai_engine else False,
    ai_calls=ai_engine.stats["calls"] if ai_engine else 0
)


# ─────────────────────────────────────────────
# تنفيذ التحليل
# ─────────────────────────────────────────────
if start_btn:

    if not my_file:
        st.error("❌ الرجاء رفع ملف منتجاتك أولاً")
        st.stop()

    if not comp_files:
        st.error("❌ الرجاء رفع ملفات المنافسين")
        st.stop()

    # قراءة ملفي
    df_my = read_uploaded_file(my_file)
    if df_my is None:
        st.error("❌ تعذر قراءة ملف منتجاتك")
        st.stop()

    my_products = extract_products(df_my, is_my_file=True)

    # قراءة ملفات المنافسين
    competitors_data = {}
    for f in comp_files:
        df = read_uploaded_file(f)
        if df is None:
            st.warning(f"⚠️ تعذر قراءة ملف: {f.name}")
            continue
        competitors_data[f.name] = extract_products(df)

    session_id = generate_session_id()

    progress = st.progress(0)
    status = st.empty()

    all_results = {}
    total_files = len(competitors_data)
    file_idx = 0

    for comp_name, comp_products in competitors_data.items():
        file_idx += 1

        def update_progress(p, msg):
            progress.progress(p)
            status.write(f"📊 {msg}")

        results = run_full_analysis(
            my_products=my_products,
            competitor_products=comp_products,
            competitor_name=comp_name,
            db=db,
            ai=ai_engine,
            session_id=session_id,
            progress_callback=update_progress
        )

        all_results[comp_name] = results

        progress.progress(file_idx / total_files)
        status.write(f"📁 اكتمل تحليل {comp_name}")

    st.success("🎉 اكتمل التحليل بالكامل!")


    # ─────────────────────────────────────────────
    # عرض الإحصائيات العامة
    # ─────────────────────────────────────────────
    total_stats = {
        "higher": 0,
        "lower": 0,
        "equal": 0,
        "review": 0,
        "missing": 0,
        "price_changes": 0,
    }

    for comp, res in all_results.items():
        for k in total_stats:
            total_stats[k] += res["stats"].get(k, 0)

    render_stats_cards(total_stats)


    # ─────────────────────────────────────────────
    # عرض النتائج لكل منافس
    # ─────────────────────────────────────────────
    st.header("📦 النتائج التفصيلية")

    for comp, res in all_results.items():
        st.subheader(f"🏪 {comp}")

        # أعلى
        if res["higher"]:
            st.markdown("### 🔴 سعرك أعلى")
            for item in res["higher"]:
                st.markdown(render_product_card(
                    name=item["my_name"],
                    my_price=item["my_price"],
                    competitors={item["competitor"]: item["comp_price"]},
                    product_no=item["product_no"],
                    brand=item["brand"],
                    ai_suggested=None
                ), unsafe_allow_html=True)

        # أقل
        if res["lower"]:
            st.markdown("### 🟢 سعرك أقل")
            for item in res["lower"]:
                st.markdown(render_product_card(
                    name=item["my_name"],
                    my_price=item["my_price"],
                    competitors={item["competitor"]: item["comp_price"]},
                    product_no=item["product_no"],
                    brand=item["brand"],
                    ai_suggested=None
                ), unsafe_allow_html=True)

        # مساوي
        if res["equal"]:
            st.markdown("### 🔵 سعر متطابق")
            for item in res["equal"]:
                st.markdown(render_product_card(
                    name=item["my_name"],
                    my_price=item["my_price"],
                    competitors={item["competitor"]: item["comp_price"]},
                    product_no=item["product_no"],
                    brand=item["brand"],
                    ai_suggested=None
                ), unsafe_allow_html=True)

        # مراجعة
        if res["review"]:
            st.markdown("### ⚠️ يحتاج مراجعة")
            for item in res["review"]:
                st.markdown(render_product_card(
                    name=item["my_name"],
                    my_price=item["my_price"],
                    competitors={item["competitor"]: item["comp_price"]},
                    product_no=item["product_no"],
                    brand=item["brand"],
                    ai_suggested=None
                ), unsafe_allow_html=True)

        # مفقود
        if res["missing"]:
            st.markdown("### 🟡 منتجات مفقودة")
            for item in res["missing"]:
                st.info(f"❗ {item['comp_name']} — {item['comp_price']} ريال — {item['competitor']}")


    # ─────────────────────────────────────────────
    # إرسال النتائج إلى Make.com
    # ─────────────────────────────────────────────
    st.header("🔗 إرسال النتائج إلى Make.com")

    if st.button("📤 إرسال تحديثات الأسعار"):
        all_updates = []
        for comp, res in all_results.items():
            all_updates.extend(res["higher"])
            all_updates.extend(res["lower"])
        r = send_price_updates(WEBHOOK_UPDATE_PRICES, all_updates, session_id)
        st.write(r)

    if st.button("📤 إرسال المنتجات المفقودة"):
        all_missing = []
        for comp, res in all_results.items():
            all_missing.extend(res["missing"])
        r = send_missing_products(WEBHOOK_NEW_PRODUCTS, all_missing, session_id)
        st.write(r)

    if st.button("📤 إرسال تقرير كامل"):
        r = send_full_report(WEBHOOK_REPORT, total_stats, session_id)
        st.write(r)
