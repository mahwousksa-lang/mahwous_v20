"""
🧪 مهووس v21 — نظام التسعير الذكي الكامل
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ محرك مطابقة 5 طبقات (بصمة → alias → حقول → AI → fallback)
✅ Gemini AI للحالات الغامضة + اقتراح أسعار ذكية
✅ Make.com Webhooks لإرسال التحديثات
✅ ذاكرة تراكمية لا تنسى (11 جدول SQLite)
✅ تحقق المفقودات — هل موجود عندك باسم آخر؟
✅ ترحيل منظم — معلق → مرسل → مؤكد
✅ بطاقة منتج مرئية مع كل المنافسين + شريط السعر
✅ شريط تقدم تفصيلي مع خطوات واضحة
"""
import streamlit as st
import pandas as pd
import os, sys, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import COLORS, MATCH_THRESHOLDS
from styles import inject_css, render_header, render_stats_cards, render_product_card
from utils.db_manager import DatabaseManager
from utils.helpers import (
    read_uploaded_file, extract_products, generate_session_id,
    format_price, products_to_dataframe, to_excel_bytes, to_csv_bytes
)
from utils.webhook_helper import send_price_updates, send_missing_products, send_full_report
from engines.smart_engine import SmartEngineV21
from engines.ai_engine import AIEngine

# ═══════════════════════════════════════════════════
# إعداد الصفحة
# ═══════════════════════════════════════════════════
st.set_page_config(
    page_title="مهووس v21 🧪",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

# ═══════════════════════════════════════════════════
# تهيئة الموارد
# ═══════════════════════════════════════════════════
@st.cache_resource
def init_db():
    return DatabaseManager("data/mahwous.db")

def init_ai(api_keys):
    return AIEngine(api_keys=api_keys if api_keys else [])

def init_engine(db, ai):
    return SmartEngineV21(db=db, ai_engine=ai)

db = init_db()

# تهيئة session state
for key, val in [
    ("results", None), ("all_results", []), ("session_id", ""),
    ("results_stats", {}), ("gemini_keys", []),
    ("webhook_prices", ""), ("webhook_missing", ""), ("webhook_report", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ═══════════════════════════════════════════════════
# الشريط الجانبي
# ═══════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:16px 0 8px">
        <div style="font-size:2.8rem">🧪</div>
        <div style="font-size:1.3rem;font-weight:800;background:linear-gradient(90deg,#6C63FF,#4ade80);-webkit-background-clip:text;-webkit-text-fill-color:transparent">مهووس v21</div>
        <div style="font-size:0.78rem;color:#64748b;margin-top:4px">AI + ذاكرة عبقرية</div>
    </div>""", unsafe_allow_html=True)

    # ─── إعدادات AI ───
    with st.expander("🤖 إعدادات Gemini AI", expanded=False):
        keys_input = st.text_area(
            "مفاتيح Gemini API (سطر لكل مفتاح)",
            value="\n".join(st.session_state.gemini_keys),
            height=100,
            placeholder="AIza..."
        )
        if keys_input.strip():
            new_keys = [k.strip() for k in keys_input.strip().split("\n") if k.strip()]
            if new_keys != st.session_state.gemini_keys:
                st.session_state.gemini_keys = new_keys
        
        ai_test = init_ai(st.session_state.gemini_keys)
        if ai_test.available:
            st.markdown(f'<div class="success-box">✅ Gemini متاح — {len(st.session_state.gemini_keys)} مفتاح</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">⚠️ أدخل مفتاح Gemini للمطابقة الذكية المحسّنة</div>', unsafe_allow_html=True)

    # ─── إعدادات Webhooks ───
    with st.expander("🔗 Webhooks (Make.com)", expanded=False):
        st.session_state.webhook_prices = st.text_input(
            "🔴 webhook تحديث الأسعار",
            value=st.session_state.webhook_prices,
            placeholder="https://hook.eu1.make.com/..."
        )
        st.session_state.webhook_missing = st.text_input(
            "🔵 webhook المنتجات المفقودة",
            value=st.session_state.webhook_missing,
            placeholder="https://hook.eu1.make.com/..."
        )
        st.session_state.webhook_report = st.text_input(
            "📊 webhook التقرير الكامل",
            value=st.session_state.webhook_report,
            placeholder="https://hook.eu1.make.com/..."
        )

    st.markdown("---")

    # ─── إحصائيات الذاكرة ───
    stats_db = db.get_stats()
    if stats_db.get("total_sessions", 0) > 0:
        st.markdown("**📊 الذاكرة التراكمية**")
        for label, key, color in [
            ("🏷️ مرجعية", "total_master", "#a5b4fc"),
            ("🏪 منتجاتك", "total_my", "#4ade80"),
            ("👥 منافسين", "total_competitors", "#60a5fa"),
            ("📈 أسعار", "total_prices", "#fbbf24"),
            ("🔵 مفقود", "total_missing", "#60a5fa"),
            ("🧠 أسماء بديلة", "total_aliases", "#c4b5fd"),
        ]:
            val = stats_db.get(key, 0)
            st.markdown(f'<div class="sidebar-stat"><span style="color:#64748b">{label}</span><span class="val" style="color:{color}">{val:,}</span></div>', unsafe_allow_html=True)
        st.markdown("")

    st.markdown("---")
    st.markdown("### 📂 رفع الملفات")
    my_file = st.file_uploader("📦 ملف مهووس (منتجاتك)", type=["xlsx","xls","csv"], key="my_file")
    comp_files = st.file_uploader("🏪 ملفات المنافسين", type=["xlsx","xls","csv"],
                                   accept_multiple_files=True, key="comp_files")

    if my_file:
        st.markdown(f'<div class="success-box" style="font-size:.8rem">✅ {my_file.name}</div>', unsafe_allow_html=True)
    if comp_files:
        st.markdown(f'<div class="info-box" style="font-size:.8rem">📂 {len(comp_files)} ملف منافس</div>', unsafe_allow_html=True)

    st.markdown("---")
    analyze_btn = st.button(
        "🚀 بدء التحليل الذكي",
        use_container_width=True, type="primary",
        disabled=not (my_file and comp_files)
    )
    
    if st.session_state.results:
        if st.button("🗑️ مسح النتائج الحالية", use_container_width=True):
            st.session_state.results = None
            st.session_state.all_results = []
            st.rerun()

# ─── تهيئة الـ Engine ───
ai_engine = init_ai(st.session_state.gemini_keys)
engine = init_engine(db, ai_engine)

render_header(ai_available=ai_engine.available, ai_calls=ai_engine.stats.get("calls", 0))

# ═══════════════════════════════════════════════════
# التحليل مع شريط تقدم تفصيلي
# ═══════════════════════════════════════════════════
if analyze_btn and my_file and comp_files:
    session_id = generate_session_id()
    
    # ─── شريط التقدم التفصيلي ───
    progress_container = st.container()
    with progress_container:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚙️ جاري التحليل...</div>', unsafe_allow_html=True)
        
        steps = [
            ("📖 قراءة ملف مهووس", "active"),
            ("🔍 تحليل المنافسين", "pending"),
            ("🤖 معالجة AI", "pending"),
            ("💾 حفظ في الذاكرة", "pending"),
            ("✅ اكتمل!", "pending"),
        ]
        steps_placeholder = st.empty()
        
        def render_steps(current_step, statuses=None):
            html = ""
            icons = ["📖","🔍","🤖","💾","✅"]
            labels = ["قراءة ملف مهووس","تحليل المنافسين","معالجة AI","حفظ في الذاكرة","اكتمل!"]
            for i, (icon, label) in enumerate(zip(icons, labels)):
                if statuses:
                    cls = statuses[i]
                elif i < current_step:
                    cls = "step-done"
                elif i == current_step:
                    cls = "step-active"
                else:
                    cls = "step-pending"
                icon_show = "✅" if cls == "step-done" else ("⏳" if cls == "step-active" else icon)
                html += f'<div class="progress-step"><div class="step-icon {cls}">{icon_show}</div><div style="color:{"#4ade80" if cls=="step-done" else ("#a5b4fc" if cls=="step-active" else "#475569")}">{label}</div></div>'
            steps_placeholder.markdown(html, unsafe_allow_html=True)
        
        render_steps(0)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # خطوة 1: قراءة ملف مهووس
    with st.spinner(""):
        my_df = read_uploaded_file(my_file)
        if my_df is None or my_df.empty:
            st.error("❌ لم يتم التعرف على ملف مهووس"); st.stop()
        my_products = extract_products(my_df, is_my_file=True)
        if not my_products:
            st.error("❌ لم يتم العثور على منتجات في ملف مهووس"); st.stop()
    
    render_steps(1)
    progress_bar.progress(10)
    status_text.markdown(f'✅ تم قراءة **{len(my_products):,}** منتج من مهووس')

    all_results = []
    combined = {"higher":[], "lower":[], "equal":[], "missing":[], "review":[], "price_changes":[]}
    combined_stats = {"total_my": len(my_products), "total_comp": 0}
    ai_calls_total = 0

    # خطوة 2 + 3: تحليل كل منافس
    for file_idx, comp_file in enumerate(comp_files):
        comp_name = os.path.splitext(comp_file.name)[0]
        base_pct = 10 + (file_idx / len(comp_files)) * 70

        status_text.markdown(f'🔍 تحليل: **{comp_name}** ({file_idx+1}/{len(comp_files)})')
        render_steps(1)
        
        comp_df = read_uploaded_file(comp_file)
        if comp_df is None or comp_df.empty:
            st.warning(f"⚠️ تعذر قراءة {comp_name}"); continue
        comp_products = extract_products(comp_df)
        if not comp_products:
            st.warning(f"⚠️ لا منتجات في {comp_name}"); continue
        combined_stats["total_comp"] += len(comp_products)

        # تحديث التقدم أثناء التحليل
        def update_progress(pct, msg):
            total_pct = int(base_pct + pct * 70 / len(comp_files))
            progress_bar.progress(min(total_pct / 100, 0.85))
            if ai_engine.available and ai_engine.stats["calls"] > 0:
                render_steps(2)  # AI نشط

        results = engine.analyze(
            my_products, comp_products, comp_name,
            session_id=session_id,
            progress_callback=update_progress
        )
        
        ai_calls_total += results.get("ai_stats", {}).get("calls", 0)
        all_results.append({"competitor": comp_name, "results": results})
        for key in combined:
            combined[key].extend(results.get(key, []))

    # خطوة 4: حفظ
    render_steps(3)
    progress_bar.progress(90)
    status_text.markdown("💾 جاري الحفظ في الذاكرة...")

    combined_stats.update({
        "matched": len(combined["higher"]) + len(combined["lower"]) + len(combined["equal"]),
        "higher": len(combined["higher"]), "lower": len(combined["lower"]),
        "equal": len(combined["equal"]), "missing": len(combined["missing"]),
        "review": len(combined["review"]), "price_changes": len(combined["price_changes"]),
    })

    db.create_session(session_id, {
        "my_file": my_file.name,
        "competitor_files": [f.name for f in comp_files],
        "total_my": combined_stats["total_my"],
        "total_matched": combined_stats["matched"],
        "total_higher": combined_stats["higher"], "total_lower": combined_stats["lower"],
        "total_equal": combined_stats["equal"], "total_missing": combined_stats["missing"],
    })

    st.session_state.results = combined
    st.session_state.results_stats = combined_stats
    st.session_state.all_results = all_results
    st.session_state.session_id = session_id

    # خطوة 5: إرسال Webhook تلقائي إذا مُعدّ
    if st.session_state.webhook_report:
        send_full_report(st.session_state.webhook_report, combined_stats, session_id)

    # اكتمل
    render_steps(-1, ["step-done","step-done","step-done","step-done","step-done"])
    progress_bar.progress(100)
    ai_msg = f" | 🤖 AI: {ai_calls_total} استدعاء" if ai_calls_total > 0 else ""
    status_text.markdown(f'✅ **اكتمل التحليل** — {len(comp_files)} منافس | {combined_stats["matched"]:,} منتج متطابق{ai_msg}')

# ═══════════════════════════════════════════════════
# عرض النتائج
# ═══════════════════════════════════════════════════
if st.session_state.results:
    results = st.session_state.results
    stats = st.session_state.get("results_stats", {})
    render_stats_cards(stats)

    if results.get("price_changes"):
        st.markdown(f'<div class="warning-box">📢 <strong>{len(results["price_changes"])}</strong> تغيير في أسعار المنافسين منذ آخر تحليل!</div>', unsafe_allow_html=True)

    tabs = st.tabs([
        f"🔴 أعلى ({stats.get('higher',0)})",
        f"🟢 أقل ({stats.get('lower',0)})",
        f"✅ متطابق ({stats.get('equal',0)})",
        f"🔵 مفقود ({stats.get('missing',0)})",
        f"⚠️ مراجعة ({stats.get('review',0)})",
        "📦 ترحيل",
        "🔍 تحقق",
        "📊 مقارنة",
        "🔗 Webhooks",
        "📋 سجل",
    ])

    # ─── Helper: بناء product_map ───
    def build_product_map(cat_items, all_results_data):
        pmap = {}
        for item in cat_items:
            fp = item.get("fingerprint", "")
            if fp not in pmap:
                pmap[fp] = {
                    "my_name": item.get("my_name",""),
                    "my_price": item.get("my_price", 0),
                    "product_no": item.get("product_no",""),
                    "brand": item.get("brand",""),
                    "competitors": {},
                    "items": [],
                }
            pmap[fp]["competitors"][item.get("competitor","")] = item.get("comp_price", 0)
            pmap[fp]["items"].append(item)
        # إثراء من أقسام أخرى
        for other_cat in ["higher","lower","equal"]:
            for item in all_results_data.get(other_cat, []):
                fp = item.get("fingerprint","")
                if fp in pmap:
                    pmap[fp]["competitors"][item.get("competitor","")] = item.get("comp_price", 0)
        return pmap

    def render_tab_with_cards(tab, cat, title_text):
        with tab:
            items = results.get(cat, [])
            if not items:
                st.markdown('<div class="empty-state"><div class="icon">📭</div><div class="text">لا توجد بيانات</div></div>', unsafe_allow_html=True)
                return

            pmap = build_product_map(items, results)
            
            # فلاتر
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1: search = st.text_input("🔍 بحث", key=f"srch_{cat}", placeholder="ابحث عن منتج...")
            with col2:
                brands = sorted(set(i.get("brand","") for i in items if i.get("brand")))
                brand_f = st.selectbox("الماركة", ["الكل"] + brands, key=f"brand_{cat}")
            with col3:
                sort_by = st.selectbox("ترتيب", ["الفرق%","السعر","الماركة"], key=f"sort_{cat}")

            # ترتيب
            plist = list(pmap.items())
            if sort_by == "الفرق%":
                plist.sort(key=lambda x: abs(x[1]["items"][0].get("diff_pct",0)), reverse=True)
            elif sort_by == "السعر":
                plist.sort(key=lambda x: x[1]["my_price"] or 0, reverse=True)

            # تصدير + webhook
            col_e1, col_e2, col_e3 = st.columns(3)
            df = products_to_dataframe(items, cat)
            with col_e1:
                st.download_button(f"📥 Excel", to_excel_bytes(df), f"{cat}.xlsx", use_container_width=True)
            with col_e2:
                st.download_button(f"📄 CSV", to_csv_bytes(df), f"{cat}.csv", use_container_width=True)
            if cat == "higher" and st.session_state.webhook_prices:
                with col_e3:
                    if st.button("📤 إرسال للـ Webhook", key=f"wh_{cat}", use_container_width=True):
                        r = send_price_updates(st.session_state.webhook_prices, items, st.session_state.session_id)
                        if r["success"]:
                            st.success(r["message"])
                        else:
                            st.error(r["message"])

            st.markdown(f'<div class="info-box">📊 <strong>{len(pmap)}</strong> منتج فريد | إجمالي الصفوف: <strong>{len(items)}</strong></div>', unsafe_allow_html=True)

            count = 0
            for fp, data in plist:
                if search and search.lower() not in data["my_name"].lower(): continue
                if brand_f != "الكل" and data["brand"] != brand_f: continue
                if count >= 100: break
                count += 1

                # اقتراح AI للسعر
                ai_sug = None
                if ai_engine.available and data["competitors"]:
                    ai_result = ai_engine.suggest_price(data["my_price"], data["competitors"])
                    ai_sug = ai_result.get("suggested_price")

                card_html = render_product_card(
                    data["my_name"], data["my_price"],
                    data["competitors"], data["product_no"], data["brand"],
                    ai_suggested=ai_sug
                )
                st.markdown(card_html, unsafe_allow_html=True)

            if count == 0:
                st.markdown('<div class="empty-state"><div class="icon">🔍</div><div class="text">لا نتائج للبحث</div></div>', unsafe_allow_html=True)

    render_tab_with_cards(tabs[0], "higher", "سعرك أعلى")
    render_tab_with_cards(tabs[1], "lower",  "سعرك أقل")
    render_tab_with_cards(tabs[2], "equal",  "متطابق")

    # ─── Tab 4: المفقودات ───
    with tabs[3]:
        items = results.get("missing", [])
        if items:
            has_match   = [p for p in items if p.get("possible_match_score",0) >= 40]
            truly_miss  = [p for p in items if p.get("possible_match_score",0) < 40]

            if has_match:
                st.markdown(f'<div class="warning-box">⚠️ <strong>{len(has_match)}</strong> منتج «مفقود» قد يكون موجوداً عندك باسم آخر! → تبويب «تحقق»</div>', unsafe_allow_html=True)

            # فلتر
            col1, col2 = st.columns(2)
            with col1: miss_search = st.text_input("🔍 بحث", key="miss_search")
            with col2:
                miss_brands = sorted(set(p.get("brand","") for p in truly_miss if p.get("brand")))
                miss_brand = st.selectbox("الماركة", ["الكل"]+miss_brands, key="miss_brand")

            # Webhook للمفقودات
            if st.session_state.webhook_missing:
                if st.button("📤 إرسال المفقودات للـ Webhook", key="wh_missing"):
                    r = send_missing_products(st.session_state.webhook_missing, truly_miss, st.session_state.session_id)
                    st.success(r["message"]) if r["success"] else st.error(r["message"])

            st.markdown(f'<div class="info-box">📊 مفقود فعلاً: <strong>{len(truly_miss)}</strong> | يحتاج تحقق: <strong>{len(has_match)}</strong></div>', unsafe_allow_html=True)

            seen, count = set(), 0
            for p in truly_miss:
                fp = p.get("fingerprint","")
                if fp in seen: continue
                seen.add(fp)
                if miss_search and miss_search.lower() not in p.get("comp_name","").lower(): continue
                if miss_brand != "الكل" and p.get("brand","") != miss_brand: continue
                if count >= 80: break
                count += 1

                # إثراء AI
                enrich = {}
                if ai_engine.available:
                    enrich = ai_engine.enrich_missing_product(p.get("comp_name",""))

                desc = enrich.get("description","") or ""
                gender_icon = {"men":"👨","women":"👩","unisex":"👥"}.get(enrich.get("gender",""), "")

                st.markdown(f"""<div class="pcard">
                    <div class="pcard-header">
                        <div>
                            <div class="pcard-name">{p.get('comp_name','')[:70]}</div>
                            <div class="pcard-brand">
                                {'<span class="badge badge-purple">' + enrich.get('brand', p.get('brand','')) + '</span>' if (enrich.get('brand') or p.get('brand')) else ''}
                                {gender_icon}
                                {'<span class="ai-badge">🤖 AI</span>' if enrich else ''}
                            </div>
                        </div>
                        <div style="text-align:right">
                            <div style="font-size:1.3rem;font-weight:800;color:#60a5fa">{format_price(p.get('comp_price'))}</div>
                            <div style="font-size:.75rem;color:#64748b">{p.get('competitor','')}</div>
                        </div>
                    </div>
                    {'<div class="pcard-body"><div style="color:#94a3b8;font-size:.85rem">' + desc + '</div></div>' if desc else ''}
                </div>""", unsafe_allow_html=True)

            df_m = products_to_dataframe(truly_miss, "missing")
            if not df_m.empty:
                st.download_button("📥 تصدير المفقودات Excel", to_excel_bytes(df_m), "missing.xlsx")
        else:
            st.markdown('<div class="empty-state"><div class="icon">🎉</div><div class="text">لا منتجات مفقودة</div></div>', unsafe_allow_html=True)

    # ─── Tab 5: مراجعة ───
    with tabs[4]:
        items = results.get("review", [])
        if items:
            st.markdown('<div class="warning-box">⚠️ هذه المنتجات نسبة تطابقها متوسطة. إذا أكدت، النظام يتعلم ولا يسألك مرة ثانية.</div>', unsafe_allow_html=True)
            for i, p in enumerate(items[:60]):
                conf = p.get("confidence", 0)
                ai_used = p.get("ai_used", False)
                conf_color = "#4ade80" if conf >= 75 else ("#fbbf24" if conf >= 60 else "#f87171")
                st.markdown(f"""<div class="pcard" style="border-right:4px solid {conf_color}">
                    <div class="pcard-header">
                        <div>
                            <div class="pcard-name">🏪 منتجك: {p.get('my_name','')[:60]}</div>
                            <div class="pcard-brand">↕️ المنافس: {p.get('comp_name','')[:60]}</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:1.5rem;font-weight:800;color:{conf_color}">{conf:.0f}%</div>
                            {'<div class="ai-badge">🤖</div>' if ai_used else ''}
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ نفس المنتج", key=f"rv_y_{i}", use_container_width=True):
                        fp = p.get("fingerprint","")
                        master = db.conn.execute("SELECT id FROM master_products WHERE fingerprint=?", (fp,)).fetchone()
                        if master:
                            db.add_alias(master["id"], str(p.get("comp_name","")).strip().lower(), "manual")
                            db.log_action("manual_match", "review", details=f"أكد: {p.get('comp_name','')} = {p.get('my_name','')}")
                        st.success("✅ تعلّم النظام!"); st.rerun()
                with col2:
                    if st.button("❌ مختلف", key=f"rv_n_{i}", use_container_width=True):
                        st.info("تم التجاهل")
                with col3:
                    if ai_engine.available and not p.get("ai_used"):
                        if st.button("🤖 اسأل AI", key=f"rv_ai_{i}", use_container_width=True):
                            ai_r = ai_engine.match_products(p.get("my_name",""), p.get("comp_name",""))
                            verdict = "✅ نفسه" if ai_r.get("is_same") else "❌ مختلف"
                            st.info(f"AI: {verdict} — {ai_r.get('reason','')}")
        else:
            st.markdown('<div class="empty-state"><div class="icon">🎉</div><div class="text">لا منتجات تحتاج مراجعة</div></div>', unsafe_allow_html=True)

    # ─── Tab 6: ترحيل ───
    with tabs[5]:
        st.markdown("""<div class="section-card">
            <div class="section-title">📦 ترحيل التعديلات</div>
            <div class="info-box">
                💡 <strong>مسار الترحيل:</strong><br>
                1️⃣ <strong>ترحيل</strong> → حالة: ⏳ معلق<br>
                2️⃣ <strong>تصدير → إرسال للمتجر</strong> → حالة: 📤 مُرسل<br>
                3️⃣ <strong>تطبيق في المتجر + تأكيد</strong> → حالة: ✅ مؤكد<br>
                ⚡ كل خطوة مسجلة — لن تنسى أي تعديل أبداً
            </div>
        </div>""", unsafe_allow_html=True)

        higher_items = results.get("higher", [])
        if higher_items:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"#### 🔴 {len(higher_items)} منتج سعره أعلى — جاهز للترحيل")
            with col2:
                if st.button("📦 ترحيل الكل معلق", key="migrate_all", use_container_width=True, type="primary"):
                    cnt = 0
                    for item in higher_items:
                        my_prod = db.conn.execute("SELECT id FROM my_products WHERE fingerprint=?",
                                                  (item.get("fingerprint",""),)).fetchone()
                        if my_prod:
                            db.create_price_modification(
                                my_product_id=my_prod["id"],
                                product_no=item.get("product_no",""),
                                product_name=item.get("my_name",""),
                                old_price=item.get("my_price",0),
                                new_price=item.get("comp_price", item.get("my_price",0)),
                                reason=f"المنافس {item.get('competitor','')} أقل بـ {abs(item.get('diff',0)):.0f}",
                                competitor_name=item.get("competitor",""),
                                competitor_price=item.get("comp_price",0),
                                session_id=st.session_state.session_id
                            )
                            cnt += 1
                    st.success(f"✅ {cnt} تعديل معلق"); st.rerun()

        pending = db.get_pending_price_mods()
        if pending:
            st.markdown(f"#### ⏳ معلقة ({len(pending)})")
            for mod in pending:
                diff = mod.get("price_diff", 0)
                color = "#f87171" if diff < 0 else "#4ade80"
                st.markdown(f"""<div class="history-entry">
                    <div style="flex:3"><strong>{mod.get('my_product_name','')[:50]}</strong>
                    <div style="font-size:.78rem;color:#64748b">#{mod.get('my_product_no','')} | {mod.get('reason','')[:50]}</div></div>
                    <div>{format_price(mod.get('old_price'))} → <span style="color:{color};font-weight:700">{format_price(mod.get('new_price'))}</span></div>
                    <span class="badge badge-yellow">معلق</span>
                </div>""", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                df_mods = pd.DataFrame(pending)
                st.download_button("📥 Excel المعلقة", to_excel_bytes(df_mods), "pending.xlsx", use_container_width=True)
            with col2:
                if st.button("📤 تعليم الكل مُرسل", use_container_width=True):
                    for m in pending: db.mark_price_mod_sent(m["id"])
                    st.success("✅ مُرسل"); st.rerun()
            with col3:
                if st.button("✅ تأكيد الكل مطبّق", use_container_width=True):
                    for m in pending: db.mark_price_mod_confirmed(m["id"])
                    st.success("✅ مؤكد"); st.rerun()

        # السجل
        history = db.get_price_mod_history(40)
        if history:
            st.markdown("#### 📋 سجل التعديلات")
            status_map = {"pending":("badge-yellow","معلق"),"sent":("badge-blue","مُرسل"),"confirmed":("badge-green","مؤكد")}
            for h in history:
                bc, bt = status_map.get(h.get("status",""), ("badge-yellow","—"))
                st.markdown(f"""<div class="history-entry">
                    <div style="flex:3"><strong>{h.get('my_product_name','')[:45]}</strong> <small style="color:#64748b">#{h.get('my_product_no','')}</small></div>
                    <div style="white-space:nowrap">{format_price(h.get('old_price'))} → {format_price(h.get('new_price'))}</div>
                    <span class="badge {bc}">{bt}</span>
                    <div class="date">{str(h.get('created_at',''))[:16]}</div>
                </div>""", unsafe_allow_html=True)

    # ─── Tab 7: تحقق المفقودات ───
    with tabs[6]:
        st.markdown("""<div class="section-card">
            <div class="section-title">🔍 تحقق المفقودات</div>
            <div class="info-box">
                💡 النظام اكتشف منتجات «مفقودة» لكن قد تكون موجودة عندك باسم آخر<br>
                • <strong>✅ نعم نفسه</strong>: يُحذف من المفقودات + النظام يتعلم الاسم البديل<br>
                • <strong>❌ لا مختلف</strong>: يبقى مفقوداً فعلاً<br>
                • <strong>🤖 اسأل AI</strong>: Gemini يحكم بدلاً عنك
            </div>
        </div>""", unsafe_allow_html=True)

        needs_review = db.get_missing_needing_review(50)
        if needs_review:
            st.markdown(f"#### ⚠️ تحتاج قرارك ({len(needs_review)})")
            for i, m in enumerate(needs_review):
                score = m.get("possible_match_score", 0)
                sc = "#4ade80" if score >= 70 else ("#fbbf24" if score >= 50 else "#f87171")
                st.markdown(f"""<div class="pcard">
                    <div class="pcard-header">
                        <div>
                            <div class="pcard-name">❓ {m.get('raw_name','')[:65]}</div>
                            <div class="pcard-brand">المنافس: {m.get('competitor_name','')} | {format_price(m.get('competitor_price'))}</div>
                        </div>
                        <span class="badge badge-yellow">تحقق مطلوب</span>
                    </div>
                    <div class="pcard-body">
                        <div style="background:rgba(245,158,11,.05);border-radius:8px;padding:10px 14px">
                            <div style="color:#fbbf24;font-size:.85rem;margin-bottom:6px">🔎 أقرب منتج عندك:</div>
                            <div style="display:flex;justify-content:space-between;align-items:center">
                                <div style="color:#e2e8f0;font-weight:600">{m.get('possible_match_name','غير معروف')[:60]}</div>
                                <div style="text-align:center">
                                    <div style="font-size:1.6rem;font-weight:800;color:{sc}">{score:.0f}%</div>
                                    <div style="font-size:.7rem;color:#64748b">تشابه</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("✅ نعم نفسه", key=f"dup_{m['id']}_{i}", use_container_width=True):
                        db.verify_missing_is_duplicate(m["id"], m.get("possible_match_fp",""))
                        st.success("✅ تعلّم النظام!"); st.rerun()
                with col2:
                    if st.button("❌ لا مختلف", key=f"conf_{m['id']}_{i}", use_container_width=True):
                        db.verify_missing_confirmed(m["id"]); st.rerun()
                with col3:
                    if st.button("🚫 تجاهل", key=f"ign_{m['id']}_{i}", use_container_width=True):
                        db.mark_missing_ignored(m["id"], "تجاهل"); st.rerun()
                with col4:
                    if ai_engine.available:
                        if st.button("🤖 AI يحكم", key=f"ai_{m['id']}_{i}", use_container_width=True):
                            ai_r = ai_engine.match_products(
                                m.get("possible_match_name",""),
                                m.get("raw_name","")
                            )
                            if ai_r.get("is_same"):
                                db.verify_missing_is_duplicate(m["id"], m.get("possible_match_fp",""))
                                st.success(f"🤖 AI: نفسه ({ai_r.get('confidence',0):.0f}%) — {ai_r.get('reason','')}"); st.rerun()
                            else:
                                db.verify_missing_confirmed(m["id"])
                                st.info(f"🤖 AI: مختلف — {ai_r.get('reason','')}"); st.rerun()
        else:
            st.markdown('<div class="success-box">✅ لا توجد منتجات تحتاج تحقق</div>', unsafe_allow_html=True)

        # ترحيل المفقودات المؤكدة
        st.markdown("---")
        confirmed_miss = db.get_missing_products("verified_missing", 50)
        if confirmed_miss:
            st.markdown(f"#### 🔵 مفقود مؤكد جاهز للإضافة ({len(confirmed_miss)})")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📦 ترحيل كل المؤكدة للمتجر", key="migrate_miss", type="primary", use_container_width=True):
                    cnt = 0
                    for m in confirmed_miss:
                        db.mark_missing_added_to_store(m["id"]); cnt += 1
                    st.success(f"✅ {cnt} منتج مُرحَّل"); st.rerun()
            with col2:
                miss_df = pd.DataFrame([{
                    "الاسم": m.get("raw_name",""),
                    "الماركة": m.get("brand",""),
                    "السعر المقترح": m.get("competitor_price",0),
                } for m in confirmed_miss])
                st.download_button("📥 Excel المفقودات المؤكدة", to_excel_bytes(miss_df), "verified_missing.xlsx", use_container_width=True)

            for m in confirmed_miss:
                try: comps = json.loads(m.get("competitors_list","[]"))
                except: comps = []
                st.markdown(f"""<div class="history-entry">
                    <div style="flex:3"><strong>{m.get('raw_name','')[:55]}</strong><br>
                    <small style="color:#64748b">ماركة: {m.get('brand','—')} | {len(comps)} منافسين | أهمية: {m.get('importance_score',0):.0f}%</small></div>
                    <div style="color:#60a5fa;font-weight:700">{format_price(m.get('competitor_price'))}</div>
                    <span class="badge badge-blue">مؤكد</span>
                </div>""", unsafe_allow_html=True)

        # المكررة
        dups = db.get_missing_products("is_duplicate", 15)
        if dups:
            st.markdown("---")
            st.markdown("#### 🔄 مكشوفة كمكررة")
            for d in dups:
                st.markdown(f"""<div class="history-entry">
                    <div>🔄 <strong>{d.get('raw_name','')[:45]}</strong></div>
                    <div style="color:#64748b">= {d.get('possible_match_name','')[:35] or '—'}</div>
                    <span class="badge badge-purple">مكرر</span>
                </div>""", unsafe_allow_html=True)

    # ─── Tab 8: مقارنة بصرية ───
    with tabs[7]:
        st.markdown('<div class="section-card"><div class="section-title">📊 مقارنة بصرية — كل منافس لنفس المنتج</div></div>', unsafe_allow_html=True)

        all_items = results.get("higher",[]) + results.get("lower",[]) + results.get("equal",[])
        if all_items:
            big_map = {}
            for item in all_items:
                fp = item.get("fingerprint","")
                if fp not in big_map:
                    big_map[fp] = {"my_name": item.get("my_name",""), "my_price": item.get("my_price",0),
                                   "product_no": item.get("product_no",""), "brand": item.get("brand",""), "competitors":{}}
                big_map[fp]["competitors"][item.get("competitor","")] = item.get("comp_price",0)

            # فلتر: فقط منتجات بأكثر من منافس واحد
            col1, col2 = st.columns(2)
            with col1: min_comps = st.slider("الحد الأدنى لعدد المنافسين", 1, min(10, len(st.session_state.all_results) or 1), 2)
            with col2: cmp_search = st.text_input("🔍 بحث", key="cmp_srch")

            multi = {fp: d for fp, d in big_map.items() if len(d["competitors"]) >= min_comps}
            st.markdown(f'<div class="info-box">📊 <strong>{len(multi)}</strong> منتج عند {min_comps}+ منافسين</div>', unsafe_allow_html=True)

            count = 0
            for fp, data in sorted(multi.items(), key=lambda x: len(x[1]["competitors"]), reverse=True):
                if cmp_search and cmp_search.lower() not in data["my_name"].lower(): continue
                if count >= 60: break
                count += 1
                card = render_product_card(data["my_name"], data["my_price"], data["competitors"],
                                           data["product_no"], data["brand"])
                st.markdown(card, unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state"><div class="icon">📊</div><div class="text">لا بيانات — قم بتشغيل تحليل أولاً</div></div>', unsafe_allow_html=True)

    # ─── Tab 9: Webhooks ───
    with tabs[8]:
        st.markdown('<div class="section-card"><div class="section-title">🔗 إرسال البيانات — Make.com Webhooks</div></div>', unsafe_allow_html=True)

        wh_prices = st.text_input("🔴 Webhook تحديث الأسعار", value=st.session_state.webhook_prices, key="wh_p_tab")
        wh_missing = st.text_input("🔵 Webhook المنتجات المفقودة", value=st.session_state.webhook_missing, key="wh_m_tab")
        wh_report = st.text_input("📊 Webhook التقرير الكامل", value=st.session_state.webhook_report, key="wh_r_tab")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📤 إرسال الأسعار الأعلى", use_container_width=True, disabled=not wh_prices):
                r = send_price_updates(wh_prices, results.get("higher",[]), st.session_state.session_id)
                st.success(r["message"]) if r["success"] else st.error(r["message"])
        with col2:
            if st.button("📤 إرسال المفقودات", use_container_width=True, disabled=not wh_missing):
                r = send_missing_products(wh_missing, results.get("missing",[]), st.session_state.session_id)
                st.success(r["message"]) if r["success"] else st.error(r["message"])
        with col3:
            if st.button("📊 إرسال تقرير كامل", use_container_width=True, disabled=not wh_report):
                r = send_full_report(wh_report, stats, st.session_state.session_id)
                st.success(r["message"]) if r["success"] else st.error(r["message"])

        if ai_engine.available:
            st.markdown(f'<div class="ai-box">🤖 <strong>Gemini AI:</strong> {ai_engine.stats["calls"]} استدعاء | {ai_engine.stats["cache_size"]} مخزن في cache | مفتاح {ai_engine.stats["active_key"]}/{ai_engine.stats["total_keys"]}</div>', unsafe_allow_html=True)

    # ─── Tab 10: سجل الإجراءات ───
    with tabs[9]:
        st.markdown('<div class="section-card"><div class="section-title">📋 سجل الإجراءات والذاكرة الكاملة</div></div>', unsafe_allow_html=True)

        full_stats = db.get_stats()
        st.markdown(f"""<div class="stat-grid">
            <div class="stat-card purple"><div class="number">{full_stats['total_master']:,}</div><div class="label">منتج مرجعي</div></div>
            <div class="stat-card cyan"><div class="number">{full_stats['total_aliases']:,}</div><div class="label">أسماء بديلة</div></div>
            <div class="stat-card green"><div class="number">{full_stats['total_prices']:,}</div><div class="label">سعر مسجل</div></div>
            <div class="stat-card yellow"><div class="number">{full_stats['total_actions']:,}</div><div class="label">إجراء مسجل</div></div>
            <div class="stat-card blue"><div class="number">{full_stats['total_missing_added']:,}</div><div class="label">أُضيف للمتجر</div></div>
            <div class="stat-card red"><div class="number">{full_stats['total_sessions']:,}</div><div class="label">جلسة تحليل</div></div>
        </div>""", unsafe_allow_html=True)

        action_filter = st.selectbox("فلتر", [
            "الكل","manual_match","missing_is_duplicate","missing_verified",
            "missing_added_to_store","missing_ignored","price_mod_created","price_mod_sent","price_mod_confirmed"
        ], key="act_f")
        f = None if action_filter == "الكل" else action_filter
        actions = db.get_action_log(60, f)

        icons_map = {
            "manual_match":"🤝","missing_is_duplicate":"🔄","missing_verified":"✅",
            "missing_added_to_store":"📦","missing_ignored":"🚫","price_mod_created":"💰",
            "price_mod_sent":"📤","price_mod_confirmed":"✅",
        }
        labels_map = {
            "manual_match":"تأكيد تطابق","missing_is_duplicate":"كشف مكرر",
            "missing_verified":"تأكيد مفقود","missing_added_to_store":"إضافة للمتجر",
            "missing_ignored":"تجاهل","price_mod_created":"تعديل سعر",
            "price_mod_sent":"إرسال تعديل","price_mod_confirmed":"تأكيد تعديل",
        }

        if actions:
            for a in actions:
                icon = icons_map.get(a.get("action",""), "📝")
                label = labels_map.get(a.get("action",""), a.get("action",""))
                st.markdown(f"""<div class="history-entry">
                    <div>{icon} <strong>{label}</strong></div>
                    <div style="flex:2;color:#94a3b8;font-size:.82rem">{str(a.get('details','') or '')[:80]}</div>
                    <div class="date">{str(a.get('created_at',''))[:16]}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("لا إجراءات مسجلة")

        st.markdown("#### 📋 الجلسات الأخيرة")
        sessions = db.get_recent_sessions(15)
        for s in sessions:
            st.markdown(f"""<div class="history-entry">
                <div style="flex:2">📋 <strong>{s['id']}</strong><br><small style="color:#64748b">{s.get('my_file','')}</small></div>
                <div style="font-size:.8rem">✅{s.get('total_matched',0)} | 🔴{s.get('total_higher',0)} | 🟢{s.get('total_lower',0)} | 🔵{s.get('total_missing',0)}</div>
                <div class="date">{str(s.get('created_at',''))[:16]}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# الشاشة الرئيسية (بدون نتائج)
# ═══════════════════════════════════════════════════
elif not st.session_state.results:
    col1, col2, col3, col4 = st.columns(4)
    features = [
        ("🧠", "#a5b4fc", "محرك 5 طبقات", "بصمة → alias → حقول → AI → fallback\nدقة عالية + تعلم تراكمي"),
        ("🤖", "#c4b5fd", "Gemini AI", "يحكم في الحالات الغامضة\nاقتراح أسعار ذكية + إثراء المفقودات"),
        ("🔗", "#60a5fa", "Make.com Webhooks", "إرسال تحديثات الأسعار\nوالمفقودات مباشرة لمتجرك"),
        ("💾", "#4ade80", "ذاكرة لا تنسى", "11 جدول تراكمي + سجل إجراءات\nكل قرار وتعديل محفوظ"),
    ]
    for col, (icon, color, title, desc) in zip([col1,col2,col3,col4], features):
        with col:
            st.markdown(f"""<div class="section-card" style="text-align:center;min-height:160px">
                <div style="font-size:2.5rem;margin-bottom:8px">{icon}</div>
                <div style="font-weight:800;color:{color};margin-bottom:8px">{title}</div>
                <div style="color:#64748b;font-size:.82rem;white-space:pre-line">{desc}</div>
            </div>""", unsafe_allow_html=True)

    # المفقودات المحفوظة
    missing_db = db.get_missing_products(limit=8)
    if missing_db:
        st.markdown("---")
        st.markdown("### 🔵 أهم المنتجات المفقودة المحفوظة")
        for m in missing_db:
            status_map = {"needs_review":("badge-yellow","مراجعة"),"verified_missing":("badge-blue","مؤكد"),
                          "added_to_store":("badge-green","أُضيف"),"is_duplicate":("badge-purple","مكرر")}
            bc, bt = status_map.get(m.get("status",""), ("badge-yellow","—"))
            st.markdown(f"""<div class="history-entry">
                <div style="flex:3"><strong>{m.get('raw_name','')[:55]}</strong><br>
                <small style="color:#64748b">{m.get('competitors_count',1)} منافسين | أهمية: {m.get('importance_score',0):.0f}%</small></div>
                <div style="color:#60a5fa;font-weight:600">{format_price(m.get('competitor_price'))}</div>
                <span class="badge {bc}">{bt}</span>
            </div>""", unsafe_allow_html=True)

    sessions = db.get_recent_sessions(5)
    if sessions:
        st.markdown("---")
        st.markdown("### 🕐 آخر التحليلات")
        for s in sessions:
            st.markdown(f"""<div class="history-entry">
                <div style="flex:2">📋 <strong>{s['id']}</strong><br><small style="color:#64748b">{s.get('my_file','')}</small></div>
                <div style="font-size:.82rem">✅{s.get('total_matched',0)} | 🔴{s.get('total_higher',0)} | 🟢{s.get('total_lower',0)} | 🔵{s.get('total_missing',0)}</div>
                <div class="date">{str(s.get('created_at',''))[:16]}</div>
            </div>""", unsafe_allow_html=True)
