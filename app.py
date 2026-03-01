"""
🧪 مهووس v20.5 — نظام التسعير الذكي بذاكرة عبقرية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ تحقق المفقودات — هل موجود عندك باسم آخر؟
✅ تتبع التعديلات — كل تعديل مسجل ومعروف حالته
✅ ترحيل البيانات — المعدّل والمفقود يُرحّل بنظام
✅ ذاكرة لا تنسى — 11 جدول + سجل إجراءات كامل
"""
import streamlit as st
import pandas as pd
import os, sys, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import COLORS, MATCH_THRESHOLDS
from styles import inject_css, render_header, render_stats_cards, render_product_row, render_product_card
from utils.db_manager import DatabaseManager
from utils.helpers import (
    read_uploaded_file, extract_products, generate_session_id,
    format_price, format_diff, products_to_dataframe,
    to_excel_bytes, to_csv_bytes
)
from engines.smart_engine import SmartEngine

st.set_page_config(page_title="مهووس v20.5", page_icon="🧪", layout="wide", initial_sidebar_state="expanded")
inject_css()

@st.cache_resource
def init_db():
    return DatabaseManager("data/mahwous.db")
@st.cache_resource
def init_engine(_db):
    return SmartEngine(db=_db)

db = init_db()
engine = init_engine(db)

if "results" not in st.session_state:
    st.session_state.results = None
if "all_results" not in st.session_state:
    st.session_state.all_results = []

# ═══════════════════════════════════════════════════
# الشريط الجانبي
# ═══════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:16px 0">
        <div style="font-size:2.5rem">🧪</div>
        <div style="font-size:1.2rem;font-weight:700;color:#a5b4fc">مهووس v20.5</div>
        <div style="font-size:0.8rem;color:#64748b">ذاكرة عبقرية — لا تنسى</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    stats = db.get_stats()
    if stats["total_sessions"] > 0:
        st.markdown(f"""<div class="info-box">
            📊 <strong>الذاكرة</strong><br>
            🏷️ مرجعية: <strong>{stats['total_master']}</strong> | 🏪 منتجاتك: <strong>{stats['total_my']}</strong><br>
            👥 منافسين: <strong>{stats['total_competitors']}</strong> | 📈 أسعار: <strong>{stats['total_prices']}</strong><br>
            🔵 مفقود: <strong>{stats['total_missing']}</strong> | ✅ أُضيف للمتجر: <strong>{stats['total_missing_added']}</strong><br>
            🔄 مكرر (تم كشفه): <strong>{stats['total_missing_dup']}</strong><br>
            🧠 أسماء بديلة: <strong>{stats['total_aliases']}</strong> | 📋 جلسات: <strong>{stats['total_sessions']}</strong><br>
            📝 إجراءات مسجلة: <strong>{stats['total_actions']}</strong><br>
            ⏳ تعديلات معلقة: <strong>{stats['pending_price_mods']}</strong> | ✅ مؤكدة: <strong>{stats['confirmed_price_mods']}</strong>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📂 رفع الملفات")
    my_file = st.file_uploader("📦 ملف مهووس (منتجاتك)", type=["xlsx","xls","csv"], key="my_file")
    comp_files = st.file_uploader("🏪 ملفات المنافسين", type=["xlsx","xls","csv"], accept_multiple_files=True, key="comp_files")
    st.markdown("---")
    analyze_btn = st.button("🚀 بدء التحليل الذكي", use_container_width=True, type="primary", disabled=not(my_file and comp_files))

render_header()

# ═══════════════════════════════════════════════════
# التحليل
# ═══════════════════════════════════════════════════
if analyze_btn and my_file and comp_files:
    session_id = generate_session_id()
    with st.spinner("📖 قراءة ملف مهووس..."):
        my_df = read_uploaded_file(my_file)
        if my_df is None or my_df.empty:
            st.error("❌ لم يتم التعرف على ملف مهووس"); st.stop()
        my_products = extract_products(my_df, is_my_file=True)
        if not my_products:
            st.error("❌ لم يتم العثور على منتجات"); st.stop()

    st.markdown(f'<div class="success-box">✅ تم قراءة <strong>{len(my_products)}</strong> منتج من مهووس</div>', unsafe_allow_html=True)

    all_results = []
    combined = {"higher":[], "lower":[], "equal":[], "missing":[], "review":[], "price_changes":[]}
    combined_stats = {"total_my": len(my_products), "total_comp": 0}
    progress_bar = st.progress(0)
    status_text = st.empty()

    for file_idx, comp_file in enumerate(comp_files):
        comp_name = os.path.splitext(comp_file.name)[0]
        status_text.markdown(f"🔍 تحليل: **{comp_name}** ({file_idx+1}/{len(comp_files)})")
        comp_df = read_uploaded_file(comp_file)
        if comp_df is None or comp_df.empty:
            st.warning(f"⚠️ تعذر قراءة {comp_name}"); continue
        comp_products = extract_products(comp_df)
        if not comp_products:
            st.warning(f"⚠️ لا منتجات في {comp_name}"); continue
        combined_stats["total_comp"] += len(comp_products)

        def update_progress(pct, msg):
            progress_bar.progress(min((file_idx + pct) / len(comp_files), 1.0))

        results = engine.analyze(my_products, comp_products, comp_name, session_id=session_id, progress_callback=update_progress)
        all_results.append({"competitor": comp_name, "results": results})
        for key in combined:
            combined[key].extend(results.get(key, []))

    progress_bar.progress(1.0); status_text.empty()

    combined_stats.update({
        "matched": len(combined["higher"])+len(combined["lower"])+len(combined["equal"]),
        "higher": len(combined["higher"]), "lower": len(combined["lower"]),
        "equal": len(combined["equal"]), "missing": len(combined["missing"]),
        "review": len(combined["review"]), "price_changes": len(combined["price_changes"]),
    })
    db.create_session(session_id, {
        "my_file": my_file.name, "competitor_files": [f.name for f in comp_files],
        "total_my": combined_stats["total_my"], "total_matched": combined_stats["matched"],
        "total_higher": combined_stats["higher"], "total_lower": combined_stats["lower"],
        "total_equal": combined_stats["equal"], "total_missing": combined_stats["missing"],
    })
    st.session_state.results = combined
    st.session_state.results_stats = combined_stats
    st.session_state.all_results = all_results
    st.session_state.session_id = session_id
    st.success(f"✅ اكتمل التحليل — الجلسة: {session_id}")

# ═══════════════════════════════════════════════════
# عرض النتائج
# ═══════════════════════════════════════════════════
if st.session_state.results:
    results = st.session_state.results
    stats = st.session_state.get("results_stats", {})
    render_stats_cards(stats)

    if results.get("price_changes"):
        st.markdown(f'<div class="warning-box">📢 تنبيه: <strong>{len(results["price_changes"])}</strong> تغيير في أسعار المنافسين!</div>', unsafe_allow_html=True)

    tabs = st.tabs([
        f"🔴 سعرك أعلى ({stats.get('higher',0)})",
        f"🟢 سعرك أقل ({stats.get('lower',0)})",
        f"✅ متطابق ({stats.get('equal',0)})",
        f"🔵 مفقود ({stats.get('missing',0)})",
        f"⚠️ مراجعة ({stats.get('review',0)})",
        "📦 ترحيل التعديلات",
        "🔍 تحقق المفقودات",
        "📋 سجل الإجراءات",
    ])

    # ─── Tab 1-3: أعلى / أقل / متطابق ───
    for tab_idx, (tab, cat, title) in enumerate([
        (tabs[0], "higher", "🔴 سعرك أعلى — فرصة خفض للتنافسية"),
        (tabs[1], "lower", "🟢 سعرك أقل — فرصة رفع للربح"),
        (tabs[2], "equal", "✅ متطابق — لا تحتاج تعديل"),
    ]):
        with tab:
            items = results.get(cat, [])
            if not items:
                st.markdown('<div class="empty-state"><div class="icon">📭</div><div class="text">لا توجد بيانات</div></div>', unsafe_allow_html=True)
                continue

            # تجميع حسب البصمة + سحب أسعار كل المنافسين
            product_map = {}
            for item in items:
                fp = item.get("fingerprint", "")
                if fp not in product_map:
                    product_map[fp] = {"my_name":item.get("my_name",""), "my_price":item.get("my_price",0), "product_no":item.get("product_no",""), "brand":item.get("brand",""), "competitors":{}, "items":[]}
                product_map[fp]["competitors"][item.get("competitor","")] = item.get("comp_price",0)
                product_map[fp]["items"].append(item)
            # إثراء: أسعار من أقسام أخرى
            for other_cat in ["higher","lower","equal"]:
                if other_cat == cat: continue
                for item in results.get(other_cat, []):
                    fp = item.get("fingerprint","")
                    if fp in product_map:
                        product_map[fp]["competitors"][item.get("competitor","")] = item.get("comp_price",0)

            # فلاتر
            col1, col2 = st.columns(2)
            with col1: search = st.text_input("🔍 بحث", key=f"s_{cat}")
            with col2:
                brands = sorted(set(p.get("brand","") for p in items if p.get("brand")))
                brand_f = st.selectbox("الماركة", ["الكل"]+brands, key=f"b_{cat}")

            st.markdown(f'<div class="info-box">📊 <strong>{len(product_map)}</strong> منتج — كل بطاقة تعرض أسعار كل المنافسين + توصية</div>', unsafe_allow_html=True)

            for fp, data in list(product_map.items())[:80]:
                if search and search.lower() not in data["my_name"].lower(): continue
                if brand_f != "الكل" and data["brand"] != brand_f: continue
                st.markdown(render_product_card(data["my_name"], data["my_price"], data["competitors"], data["product_no"], data["brand"]), unsafe_allow_html=True)

            df = products_to_dataframe(items, cat)
            c1, c2 = st.columns(2)
            with c1: st.download_button("📥 Excel", to_excel_bytes(df), f"{cat}.xlsx", use_container_width=True)
            with c2: st.download_button("📄 CSV", to_csv_bytes(df), f"{cat}.csv", use_container_width=True)

    # ─── Tab 4: المفقودات ───
    with tabs[3]:
        items = results.get("missing", [])
        if items:
            # فصل: مفقودات لها تطابق محتمل vs مفقودات جديدة
            has_match = [p for p in items if p.get("possible_match_score",0) >= 40]
            truly_missing = [p for p in items if p.get("possible_match_score",0) < 40]

            if has_match:
                st.markdown(f"""<div class="warning-box">
                    ⚠️ <strong>{len(has_match)}</strong> منتج «مفقود» لكن قد يكون موجود عندك باسم آخر!<br>
                    <small>راجعها في تبويب «🔍 تحقق المفقودات» لتأكيد أو نفي التطابق</small>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""<div class="info-box">
                📊 إجمالي: <strong>{len(items)}</strong> |
                ⚠️ يحتاج تحقق: <strong>{len(has_match)}</strong> |
                🔵 مفقود فعلاً: <strong>{len(truly_missing)}</strong>
            </div>""", unsafe_allow_html=True)

            # بدون تكرار
            seen = set()
            for p in truly_missing[:80]:
                fp = p.get("fingerprint","")
                if fp in seen: continue
                seen.add(fp)
                st.markdown(f"""<div class="product-row">
                    <div class="name"><strong>{p.get('comp_name','')[:60]}</strong><br>
                    <small style="color:#64748b">ماركة: {p.get('brand','—')} | المنافس: {p.get('competitor','')}</small></div>
                    <div style="text-align:center"><div class="price" style="color:#60a5fa">{format_price(p.get('comp_price'))}</div><small style="color:#64748b">سعر المنافس</small></div>
                    <div><span class="badge badge-blue">مفقود فعلاً</span></div>
                </div>""", unsafe_allow_html=True)

            df_m = products_to_dataframe(truly_missing, "missing")
            if not df_m.empty:
                st.download_button("📥 تصدير المفقودات", to_excel_bytes(df_m), "missing.xlsx", use_container_width=True)
        else:
            st.markdown('<div class="empty-state"><div class="icon">🎉</div><div class="text">لا منتجات مفقودة</div></div>', unsafe_allow_html=True)

    # ─── Tab 5: مراجعة ───
    with tabs[4]:
        items = results.get("review", [])
        if items:
            st.markdown('<div class="warning-box">⚠️ هذه المنتجات نسبة تطابقها متوسطة — إذا أكدت التطابق يتعلم النظام</div>', unsafe_allow_html=True)
            for i, p in enumerate(items[:50]):
                col1, col2, col3 = st.columns([4,1,1])
                with col1:
                    st.markdown(f"""<div class="product-row" style="border-right:4px solid #f59e0b;padding-right:12px">
                        <div><strong>منتجك:</strong> {p.get('my_name','')[:50]}<br>
                        <strong>المنافس:</strong> {p.get('comp_name','')[:50]}<br>
                        <small style="color:#fbbf24">ثقة: {p.get('confidence',0)}%</small></div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    if st.button("✅", key=f"rv_y_{i}", help="تأكيد التطابق"):
                        fp = p.get("fingerprint","")
                        master = db.conn.execute("SELECT id FROM master_products WHERE fingerprint=?", (fp,)).fetchone()
                        if master:
                            db.add_alias(master["id"], str(p.get("comp_name","")).strip().lower(), "manual")
                            db.log_action("manual_match", "review", details=f"أكد تطابق: {p.get('comp_name','')} = {p.get('my_name','')}")
                            st.success("✅ تم التعلم!")
                with col3:
                    if st.button("❌", key=f"rv_n_{i}", help="رفض"):
                        st.info("تم التجاهل")
        else:
            st.markdown('<div class="empty-state"><div class="icon">🎉</div><div class="text">لا منتجات تحتاج مراجعة</div></div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # Tab 6: ترحيل التعديلات
    # ═══════════════════════════════════════════════════
    with tabs[5]:
        st.markdown("""<div class="section-card"><div class="section-title">📦 ترحيل التعديلات — تتبع كل تعديل سعر وكل منتج مفقود</div></div>""", unsafe_allow_html=True)

        st.markdown("""<div class="info-box">
            💡 <strong>كيف يعمل الترحيل؟</strong><br>
            1️⃣ تحلل الملفات → النظام يكتشف الأسعار التي تحتاج تعديل<br>
            2️⃣ تختار المنتجات وتضغط «ترحيل» → تتحول لحالة «معلق»<br>
            3️⃣ تصدرها أو ترسلها للمتجر → تتحول لـ «مُرسل»<br>
            4️⃣ بعد التطبيق في المتجر → تضغط «تأكيد» → تتحول لـ «مؤكد»<br>
            ⚡ كل خطوة مسجلة — لن تنسى أي تعديل
        </div>""", unsafe_allow_html=True)

        # ─── إنشاء تعديلات من النتائج الحالية ───
        higher_items = results.get("higher", [])
        if higher_items:
            st.markdown("#### 🔴 منتجات تحتاج خفض سعر")
            if st.button("📦 ترحيل كل الأسعار الأعلى كتعديلات معلقة", key="migrate_higher"):
                count = 0
                for item in higher_items:
                    my_prod = db.conn.execute("SELECT id FROM my_products WHERE fingerprint=?", (item.get("fingerprint",""),)).fetchone()
                    if my_prod:
                        suggested = item.get("comp_price", item.get("my_price",0))
                        db.create_price_modification(
                            my_product_id=my_prod["id"],
                            product_no=item.get("product_no",""),
                            product_name=item.get("my_name",""),
                            old_price=item.get("my_price",0),
                            new_price=suggested,
                            reason=f"المنافس {item.get('competitor','')} أقل بـ {abs(item.get('diff',0))}",
                            competitor_name=item.get("competitor",""),
                            competitor_price=item.get("comp_price",0),
                            session_id=st.session_state.get("session_id","")
                        )
                        count += 1
                st.success(f"✅ تم ترحيل {count} تعديل سعر — شاهدها أدناه")
                st.rerun()

        # ─── عرض التعديلات المعلقة ───
        pending = db.get_pending_price_mods()
        if pending:
            st.markdown(f"#### ⏳ تعديلات معلقة ({len(pending)})")
            for mod in pending:
                diff = mod.get("price_diff", 0)
                color = "#f87171" if diff < 0 else "#4ade80"
                st.markdown(f"""<div class="product-row priority-urgent">
                    <div class="name"><strong>{mod.get('my_product_name','')[:50]}</strong><br>
                    <small style="color:#64748b">#{mod.get('my_product_no','')} | السبب: {mod.get('reason','')[:40]}</small></div>
                    <div style="text-align:center"><div class="price">{format_price(mod.get('old_price'))}</div><small style="color:#64748b">السعر الحالي</small></div>
                    <div style="text-align:center"><div class="price" style="color:{color}">{format_price(mod.get('new_price'))}</div><small style="color:#64748b">السعر المقترح</small></div>
                    <div><span class="badge badge-yellow">معلق</span></div>
                </div>""", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📤 تصدير التعديلات المعلقة", use_container_width=True):
                    df_mods = pd.DataFrame(pending)
                    st.download_button("📥 حمّل", to_excel_bytes(df_mods), "pending_modifications.xlsx")
            with col2:
                if st.button("✅ تعليم الكل كمُرسل", key="mark_sent", use_container_width=True):
                    for mod in pending:
                        db.mark_price_mod_sent(mod["id"])
                    st.success("✅ تم تعليم الكل كمُرسل"); st.rerun()
            with col3:
                if st.button("✅ تأكيد الكل (تم تطبيقها)", key="mark_confirmed", use_container_width=True):
                    for mod in pending:
                        db.mark_price_mod_confirmed(mod["id"])
                    st.success("✅ تم التأكيد"); st.rerun()

        # ─── سجل التعديلات ───
        history = db.get_price_mod_history(30)
        if history:
            st.markdown("#### 📋 سجل كل التعديلات")
            for h in history:
                status_badge = {"pending":"badge-yellow","sent":"badge-blue","confirmed":"badge-green"}.get(h.get("status",""), "badge-yellow")
                status_text_ar = {"pending":"معلق","sent":"مُرسل","confirmed":"مؤكد"}.get(h.get("status",""), h.get("status",""))
                st.markdown(f"""<div class="history-entry">
                    <div><strong>{h.get('my_product_name','')[:40]}</strong> <small style="color:#64748b">#{h.get('my_product_no','')}</small></div>
                    <div>{format_price(h.get('old_price'))} → {format_price(h.get('new_price'))}</div>
                    <div><span class="badge {status_badge}">{status_text_ar}</span></div>
                    <div class="date">{str(h.get('created_at',''))[:16]}</div>
                </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # Tab 7: تحقق المفقودات الذكي
    # ═══════════════════════════════════════════════════
    with tabs[6]:
        st.markdown("""<div class="section-card"><div class="section-title">🔍 تحقق المفقودات — هل هذا المنتج موجود عندك باسم آخر؟</div></div>""", unsafe_allow_html=True)

        st.markdown("""<div class="info-box">
            💡 <strong>كيف يعمل التحقق؟</strong><br>
            النظام يبحث تلقائياً عن أقرب منتج عندك لكل منتج «مفقود»<br>
            • <strong>✅ نعم نفسه:</strong> يُحذف من المفقودات + يتعلم النظام الاسم البديل<br>
            • <strong>❌ لا مختلف:</strong> يبقى مفقود فعلاً + يمكنك ترحيله للإضافة في المتجر<br>
            • <strong>🚫 تجاهل:</strong> لا تريد هذا المنتج أبداً<br>
            ⚡ بعد التأكيد، النظام لن يسألك عنه مرة ثانية
        </div>""", unsafe_allow_html=True)

        # المفقودات التي لها تطابق محتمل
        needs_review = db.get_missing_needing_review(50)
        if needs_review:
            st.markdown(f"#### ⚠️ تحتاج قرارك ({len(needs_review)})")
            for i, m in enumerate(needs_review):
                score = m.get("possible_match_score", 0)
                score_color = "#4ade80" if score >= 70 else ("#fbbf24" if score >= 50 else "#f87171")
                st.markdown(f"""<div class="pcard" style="margin:10px 0">
                    <div class="pcard-header">
                        <div>
                            <div class="pcard-name">❓ {m.get('raw_name','')[:60]}</div>
                            <div class="pcard-brand">المنافس: {m.get('competitor_name','')} | سعره: {format_price(m.get('competitor_price'))}</div>
                        </div>
                        <span class="badge badge-yellow">يحتاج تحقق</span>
                    </div>
                    <div style="padding:12px 18px;direction:rtl;background:rgba(245,158,11,0.05)">
                        <div style="margin-bottom:8px;font-weight:600;color:#fbbf24">🔎 أقرب منتج عندك:</div>
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div>
                                <div style="font-size:1rem;color:#e2e8f0;font-weight:600">{m.get('possible_match_name','غير معروف')[:60]}</div>
                            </div>
                            <div style="text-align:center">
                                <div style="font-size:1.4rem;font-weight:800;color:{score_color}">{score:.0f}%</div>
                                <div style="font-size:0.7rem;color:#64748b">نسبة التشابه</div>
                            </div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✅ نعم نفسه", key=f"dup_{m['id']}_{i}", use_container_width=True):
                        db.verify_missing_is_duplicate(m["id"], m.get("possible_match_fp",""))
                        st.success("✅ تم! النظام تعلّم — لن يعتبره مفقوداً مرة أخرى")
                        st.rerun()
                with col2:
                    if st.button(f"❌ لا مختلف", key=f"conf_{m['id']}_{i}", use_container_width=True):
                        db.verify_missing_confirmed(m["id"])
                        st.info("تم تأكيده كمفقود فعلاً")
                        st.rerun()
                with col3:
                    if st.button(f"🚫 تجاهل", key=f"ign_{m['id']}_{i}", use_container_width=True):
                        db.mark_missing_ignored(m["id"], "تجاهل من المستخدم")
                        st.rerun()
        else:
            st.markdown('<div class="success-box">✅ لا توجد منتجات تحتاج تحقق حالياً</div>', unsafe_allow_html=True)

        # ─── ترحيل المفقودات المؤكدة للمتجر ───
        st.markdown("---")
        confirmed_missing = db.get_missing_products("verified_missing", 50)
        if confirmed_missing:
            st.markdown(f"#### 🔵 مفقود مؤكد — جاهز للترحيل ({len(confirmed_missing)})")
            if st.button("📦 ترحيل كل المفقودات المؤكدة للإضافة في المتجر", key="migrate_missing"):
                count = 0
                for m in confirmed_missing:
                    db.mark_missing_added_to_store(m["id"])
                    count += 1
                st.success(f"✅ تم ترحيل {count} منتج للإضافة في المتجر")
                st.rerun()

            for m in confirmed_missing:
                try: comps = json.loads(m.get("competitors_list","[]"))
                except: comps = []
                st.markdown(f"""<div class="product-row" style="border-right:4px solid #3b82f6;padding-right:12px">
                    <div class="name"><strong>{m.get('raw_name','')[:60]}</strong><br>
                    <small style="color:#64748b">ماركة: {m.get('brand','—')} | عند {len(comps)} منافسين | أهمية: {m.get('importance_score',0):.0f}%</small></div>
                    <div style="text-align:center"><div class="price" style="color:#60a5fa">{format_price(m.get('competitor_price'))}</div></div>
                    <div><span class="badge badge-blue">مؤكد</span></div>
                </div>""", unsafe_allow_html=True)

        # ─── المفقودات التي تم ترحيلها ───
        migrations = db.get_migration_history(20)
        if migrations:
            st.markdown("---")
            st.markdown("#### ✅ تم ترحيلها للمتجر")
            for mg in migrations:
                st.markdown(f"""<div class="history-entry">
                    <div><strong>{mg.get('product_name','')[:40]}</strong></div>
                    <div>سعر مقترح: {format_price(mg.get('suggested_price'))}</div>
                    <div><span class="badge badge-green">تم الإضافة</span></div>
                    <div class="date">{str(mg.get('added_at',''))[:16]}</div>
                </div>""", unsafe_allow_html=True)

        # ─── المنتجات المكررة (تم كشفها) ───
        duplicates = db.get_missing_products("is_duplicate", 20)
        if duplicates:
            st.markdown("---")
            st.markdown("#### 🔄 تم كشفها كمكررة (موجودة عندك)")
            for d in duplicates:
                st.markdown(f"""<div class="history-entry">
                    <div>🔄 <strong>{d.get('raw_name','')[:40]}</strong></div>
                    <div style="color:#64748b">= {d.get('possible_match_name','')[:30] if d.get('possible_match_name') else 'منتج موجود'}</div>
                    <div><span class="badge badge-purple">مكرر</span></div>
                </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # Tab 8: سجل الإجراءات الكامل
    # ═══════════════════════════════════════════════════
    with tabs[7]:
        st.markdown("""<div class="section-card"><div class="section-title">📋 سجل الإجراءات — كل شيء فعلته مسجل هنا</div></div>""", unsafe_allow_html=True)

        # ─── إحصائيات الذاكرة ───
        full_stats = db.get_stats()
        st.markdown(f"""<div class="stat-grid">
            <div class="stat-card purple"><div class="number">{full_stats['total_master']}</div><div class="label">منتج مرجعي</div></div>
            <div class="stat-card cyan"><div class="number">{full_stats['total_aliases']}</div><div class="label">اسم بديل (ذاكرة)</div></div>
            <div class="stat-card green"><div class="number">{full_stats['total_prices']}</div><div class="label">سعر مسجل</div></div>
            <div class="stat-card yellow"><div class="number">{full_stats['total_actions']}</div><div class="label">إجراء مسجل</div></div>
            <div class="stat-card blue"><div class="number">{full_stats['total_missing_added']}</div><div class="label">أُضيف للمتجر</div></div>
            <div class="stat-card red"><div class="number">{full_stats['total_missing_dup']}</div><div class="label">مكرر (تم كشفه)</div></div>
        </div>""", unsafe_allow_html=True)

        action_filter = st.selectbox("فلتر الإجراءات", [
            "الكل", "manual_match", "missing_is_duplicate", "missing_verified",
            "missing_added_to_store", "missing_ignored", "price_mod_created",
            "price_mod_sent", "price_mod_confirmed"
        ], key="action_filter")

        f = None if action_filter == "الكل" else action_filter
        actions = db.get_action_log(50, f)

        action_icons = {
            "manual_match":"🤝", "missing_is_duplicate":"🔄", "missing_verified":"✅",
            "missing_added_to_store":"📦", "missing_ignored":"🚫", "price_mod_created":"💰",
            "price_mod_sent":"📤", "price_mod_confirmed":"✅",
        }
        action_labels = {
            "manual_match":"تأكيد تطابق", "missing_is_duplicate":"كشف مكرر", "missing_verified":"تأكيد مفقود",
            "missing_added_to_store":"إضافة للمتجر", "missing_ignored":"تجاهل", "price_mod_created":"تعديل سعر",
            "price_mod_sent":"إرسال تعديل", "price_mod_confirmed":"تأكيد تعديل",
        }

        if actions:
            for a in actions:
                icon = action_icons.get(a.get("action",""), "📝")
                label = action_labels.get(a.get("action",""), a.get("action",""))
                st.markdown(f"""<div class="history-entry">
                    <div>{icon} <strong>{label}</strong></div>
                    <div style="flex:2;color:#94a3b8;font-size:0.85rem">{a.get('details','') or ''}</div>
                    <div class="date">{str(a.get('created_at',''))[:16]}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("لا توجد إجراءات مسجلة بعد")

        # ─── الجلسات ───
        st.markdown("#### 📋 سجل الجلسات")
        sessions = db.get_recent_sessions(20)
        for s in sessions:
            st.markdown(f"""<div class="history-entry">
                <div>📋 <strong>{s['id']}</strong> <small style="color:#64748b"> — {s.get('my_file','')}</small></div>
                <div style="font-size:0.8rem">✅{s.get('total_matched',0)} | 🔴{s.get('total_higher',0)} | 🟢{s.get('total_lower',0)} | 🔵{s.get('total_missing',0)}</div>
                <div class="date">{str(s.get('created_at',''))[:16]}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# الحالة الأولية (بدون نتائج)
# ═══════════════════════════════════════════════════
elif not st.session_state.results:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="section-card" style="text-align:center">
            <div style="font-size:2.5rem;margin-bottom:8px">🧠</div>
            <div style="font-weight:700;color:#a5b4fc;margin-bottom:6px">ذاكرة لا تنسى</div>
            <div style="color:#64748b;font-size:0.85rem">11 جدول + سجل إجراءات<br>كل تعديل وكل قرار محفوظ<br>التعلم التراكمي يزداد ذكاءً</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="section-card" style="text-align:center">
            <div style="font-size:2.5rem;margin-bottom:8px">🔍</div>
            <div style="font-weight:700;color:#4ade80;margin-bottom:6px">تحقق المفقودات</div>
            <div style="color:#64748b;font-size:0.85rem">هل المنتج موجود باسم آخر؟<br>النظام يقترح + أنت تقرر<br>لن يسألك مرتين عن نفسه</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="section-card" style="text-align:center">
            <div style="font-size:2.5rem;margin-bottom:8px">📦</div>
            <div style="font-weight:700;color:#fbbf24;margin-bottom:6px">ترحيل منظم</div>
            <div style="color:#64748b;font-size:0.85rem">تعديل الأسعار: معلق→مرسل→مؤكد<br>المفقودات: تحقق→ترحيل→إضافة<br>كل خطوة مسجلة ومتتبعة</div>
        </div>""", unsafe_allow_html=True)

    # عرض المفقودات المسجلة
    missing_db = db.get_missing_products(limit=10)
    if missing_db:
        st.markdown("---")
        st.markdown("### 🔵 أهم المنتجات المفقودة")
        for m in missing_db:
            st.markdown(f"""<div class="product-row">
                <div class="name"><strong>{m.get('raw_name','')[:60]}</strong><br>
                <small style="color:#64748b">عند {m.get('competitors_count',1)} منافسين | أهمية: {m.get('importance_score',0):.0f}%</small></div>
                <div><span class="badge badge-{'yellow' if m.get('status')=='needs_review' else 'blue'}">{m.get('status','')}</span></div>
            </div>""", unsafe_allow_html=True)

    sessions = db.get_recent_sessions(5)
    if sessions:
        st.markdown("---")
        st.markdown("### 🕐 آخر التحليلات")
        for s in sessions:
            st.markdown(f"""<div class="history-entry">
                <div>📋 <strong>{s['id']}</strong> <small style="color:#64748b"> — {s.get('my_file','')}</small></div>
                <div style="font-size:0.8rem">✅{s.get('total_matched',0)} | 🔴{s.get('total_higher',0)} | 🟢{s.get('total_lower',0)} | 🔵{s.get('total_missing',0)}</div>
            </div>""", unsafe_allow_html=True)
