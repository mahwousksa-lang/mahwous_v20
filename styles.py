"""
مهووس v20 — التنسيقات والتصميم
"""

MAIN_CSS = """
<style>
/* ═══ Global ═══ */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');

* { font-family: 'Tajawal', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0f172a 100%);
}

/* ═══ RTL Support ═══ */
.stMarkdown, .stText, .element-container { direction: rtl; text-align: right; }
.stDataFrame { direction: ltr; }

/* ═══ Header ═══ */
.main-header {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    border: 1px solid rgba(108, 99, 255, 0.2);
    box-shadow: 0 8px 32px rgba(108, 99, 255, 0.15);
}
.main-header h1 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #c7d2fe, #a5b4fc, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.main-header p { color: #94a3b8; font-size: 0.95rem; margin: 8px 0 0 0; }

/* ═══ Stats Cards ═══ */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin: 16px 0;
}
.stat-card {
    background: rgba(30, 36, 54, 0.8);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(10px);
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.stat-card .number {
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1;
    margin: 4px 0;
}
.stat-card .label {
    font-size: 0.75rem;
    color: #8892a0;
    font-weight: 500;
}
.stat-card.red .number { color: #f87171; }
.stat-card.green .number { color: #4ade80; }
.stat-card.blue .number { color: #60a5fa; }
.stat-card.yellow .number { color: #fbbf24; }
.stat-card.purple .number { color: #a78bfa; }
.stat-card.cyan .number { color: #22d3ee; }

/* ═══ Section Cards ═══ */
.section-card {
    background: rgba(30, 36, 54, 0.6);
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
    border: 1px solid rgba(255,255,255,0.04);
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(108, 99, 255, 0.3);
}

/* ═══ Product Row ═══ */
.product-row {
    background: rgba(15, 23, 42, 0.6);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 6px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255,255,255,0.04);
    transition: background 0.2s;
    direction: rtl;
}
.product-row:hover { background: rgba(30, 36, 54, 0.8); }
.product-row .name { color: #e2e8f0; font-weight: 500; flex: 1; }
.product-row .price { font-weight: 700; font-size: 1.05rem; }
.product-row .diff {
    font-size: 0.85rem;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
}
.diff-higher { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.diff-lower { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.diff-equal { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }

/* ═══ Badge ═══ */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-red { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.badge-green { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.badge-blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.badge-yellow { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.badge-purple { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }

/* ═══ Priority Indicator ═══ */
.priority-urgent {
    border-right: 4px solid #ef4444;
    padding-right: 12px;
}
.priority-medium {
    border-right: 4px solid #f59e0b;
    padding-right: 12px;
}
.priority-low {
    border-right: 4px solid #22c55e;
    padding-right: 12px;
}

/* ═══ Tabs Styling ═══ */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(15, 23, 42, 0.5);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    color: #94a3b8;
}
.stTabs [aria-selected="true"] {
    background: rgba(108, 99, 255, 0.2) !important;
    color: #a5b4fc !important;
}

/* ═══ Buttons ═══ */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    font-family: 'Tajawal', sans-serif !important;
    transition: all 0.2s;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}

/* ═══ File Uploader ═══ */
.stFileUploader {
    border: 2px dashed rgba(108, 99, 255, 0.3) !important;
    border-radius: 12px !important;
    background: rgba(108, 99, 255, 0.03) !important;
}

/* ═══ Metric ═══ */
[data-testid="stMetricValue"] { font-family: 'Tajawal', sans-serif !important; }

/* ═══ Info Box ═══ */
.info-box {
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 10px;
    padding: 14px 18px;
    color: #93c5fd;
    font-size: 0.9rem;
    margin: 8px 0;
}
.success-box {
    background: rgba(34, 197, 94, 0.08);
    border: 1px solid rgba(34, 197, 94, 0.2);
    border-radius: 10px;
    padding: 14px 18px;
    color: #86efac;
}
.warning-box {
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.2);
    border-radius: 10px;
    padding: 14px 18px;
    color: #fcd34d;
}

/* ═══ Empty State ═══ */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #64748b;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 12px; }
.empty-state .text { font-size: 1rem; }

/* ═══ History Table ═══ */
.history-entry {
    background: rgba(15, 23, 42, 0.4);
    border-radius: 8px;
    padding: 10px 14px;
    margin: 4px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
    direction: rtl;
}
.history-entry .date { color: #64748b; font-size: 0.8rem; }

/* ═══ Progress ═══ */
.stProgress > div > div { background: linear-gradient(90deg, #6C63FF, #a78bfa) !important; }

/* ═══ Product Card (بطاقة المنتج الغنية) ═══ */
.pcard {
    background: linear-gradient(135deg, rgba(30,36,54,0.9), rgba(20,26,44,0.95));
    border-radius: 14px;
    padding: 0;
    margin: 12px 0;
    border: 1px solid rgba(255,255,255,0.06);
    overflow: hidden;
    transition: box-shadow 0.25s;
}
.pcard:hover { box-shadow: 0 8px 32px rgba(108,99,255,0.12); }

.pcard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 18px;
    background: rgba(108,99,255,0.06);
    border-bottom: 1px solid rgba(255,255,255,0.04);
    direction: rtl;
}
.pcard-header .pcard-name {
    font-weight: 700;
    color: #e2e8f0;
    font-size: 0.95rem;
    flex: 1;
}
.pcard-header .pcard-no {
    color: #64748b;
    font-size: 0.75rem;
    background: rgba(100,116,139,0.15);
    padding: 2px 8px;
    border-radius: 10px;
}
.pcard-header .pcard-brand {
    color: #a5b4fc;
    font-size: 0.75rem;
    margin-top: 2px;
}

/* شريط السعر المرجعي */
.pcard-my-price {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 18px;
    background: rgba(139,92,246,0.08);
    border-bottom: 1px solid rgba(255,255,255,0.03);
    direction: rtl;
}
.pcard-my-price .label { color: #a78bfa; font-size: 0.8rem; font-weight: 600; }
.pcard-my-price .value { color: #c4b5fd; font-size: 1.4rem; font-weight: 800; }
.pcard-my-price .sub { color: #64748b; font-size: 0.75rem; margin-right: auto; }

/* شبكة أسعار المنافسين */
.pcard-prices {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 8px;
    padding: 14px 18px;
    direction: rtl;
}
.pcard-comp {
    background: rgba(15,23,42,0.6);
    border-radius: 10px;
    padding: 10px 8px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.04);
    transition: border-color 0.2s;
    position: relative;
}
.pcard-comp:hover { border-color: rgba(108,99,255,0.3); }
.pcard-comp .comp-label {
    font-size: 0.7rem;
    color: #64748b;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.pcard-comp .comp-val {
    font-size: 1.15rem;
    font-weight: 800;
    color: #e2e8f0;
}
.pcard-comp .comp-diff {
    font-size: 0.7rem;
    font-weight: 600;
    margin-top: 3px;
    padding: 1px 6px;
    border-radius: 8px;
    display: inline-block;
}
.pcard-comp.is-lowest {
    border: 2px solid #22c55e;
    background: rgba(34,197,94,0.06);
}
.pcard-comp.is-lowest .comp-val { color: #4ade80; }
.pcard-comp.is-lowest::after {
    content: "أقل ❗";
    position: absolute;
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
    background: #22c55e;
    color: #0a0e1a;
    font-size: 0.6rem;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 6px;
}
.pcard-comp.is-highest {
    border: 2px solid rgba(239,68,68,0.4);
    background: rgba(239,68,68,0.04);
}
.pcard-comp.is-highest .comp-val { color: #f87171; }
.pcard-comp.is-me {
    border: 2px solid #a78bfa;
    background: rgba(139,92,246,0.08);
}
.pcard-comp.is-me .comp-val { color: #c4b5fd; }
.pcard-comp.is-me .comp-label { color: #a78bfa; }

/* شريط السعر البصري */
.price-bar-wrap {
    padding: 4px 18px 10px;
    direction: rtl;
}
.price-bar-track {
    height: 6px;
    background: rgba(255,255,255,0.06);
    border-radius: 3px;
    position: relative;
    margin: 6px 0;
}
.price-bar-fill {
    height: 100%;
    border-radius: 3px;
    position: absolute;
    top: 0;
}
.price-bar-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    color: #64748b;
}

/* ملخص البطاقة */
.pcard-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 18px;
    background: rgba(15,23,42,0.4);
    border-top: 1px solid rgba(255,255,255,0.03);
    font-size: 0.8rem;
    direction: rtl;
    gap: 8px;
    flex-wrap: wrap;
}
.pcard-summary .sum-item {
    display: flex;
    align-items: center;
    gap: 4px;
}
.pcard-summary .sum-label { color: #64748b; }
.pcard-summary .sum-val { font-weight: 700; }
.pcard-summary .sum-val.green { color: #4ade80; }
.pcard-summary .sum-val.red { color: #f87171; }
.pcard-summary .sum-val.blue { color: #60a5fa; }
.pcard-summary .sum-val.purple { color: #a78bfa; }

/* توصية */
.pcard-rec {
    padding: 8px 18px;
    font-size: 0.82rem;
    direction: rtl;
    border-top: 1px solid rgba(255,255,255,0.03);
}
.pcard-rec.rec-lower {
    background: rgba(239,68,68,0.06);
    color: #fca5a5;
}
.pcard-rec.rec-raise {
    background: rgba(34,197,94,0.06);
    color: #86efac;
}
.pcard-rec.rec-ok {
    background: rgba(148,163,184,0.06);
    color: #94a3b8;
}

/* ═══ Comparison Grid (Legacy) ═══ */
.comp-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 10px;
}
.comp-item {
    background: rgba(15, 23, 42, 0.5);
    border-radius: 8px;
    padding: 12px;
    text-align: center;
}
.comp-item .comp-name { color: #94a3b8; font-size: 0.8rem; }
.comp-item .comp-price { font-size: 1.3rem; font-weight: 700; color: #e2e8f0; }
.comp-item.lowest { border: 2px solid #22c55e; }
.comp-item.highest { border: 2px solid #ef4444; }

/* ═══ Scrollbar ═══ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.3); }
::-webkit-scrollbar-thumb { background: rgba(108, 99, 255, 0.3); border-radius: 3px; }

/* ═══ Hide Streamlit Branding ═══ */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
"""


def inject_css():
    """حقن CSS في الصفحة"""
    import streamlit as st
    st.markdown(MAIN_CSS, unsafe_allow_html=True)


def render_header():
    """عرض الهيدر"""
    import streamlit as st
    st.markdown("""
    <div class="main-header">
        <h1>🧪 مهووس v20 — نظام التسعير الذكي</h1>
        <p>تحليل تراكمي • مطابقة ذكية • بدون تكرار • بدون ضياع فرص</p>
    </div>
    """, unsafe_allow_html=True)


def render_stats_cards(stats):
    """عرض بطاقات الإحصائيات"""
    import streamlit as st
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card purple">
            <div class="number">{stats.get('matched', 0)}</div>
            <div class="label">✅ متطابقة</div>
        </div>
        <div class="stat-card red">
            <div class="number">{stats.get('higher', 0)}</div>
            <div class="label">🔴 سعرك أعلى</div>
        </div>
        <div class="stat-card green">
            <div class="number">{stats.get('lower', 0)}</div>
            <div class="label">🟢 سعرك أقل</div>
        </div>
        <div class="stat-card cyan">
            <div class="number">{stats.get('equal', 0)}</div>
            <div class="label">✅ نفس السعر</div>
        </div>
        <div class="stat-card blue">
            <div class="number">{stats.get('missing', 0)}</div>
            <div class="label">🔵 مفقود</div>
        </div>
        <div class="stat-card yellow">
            <div class="number">{stats.get('review', 0)}</div>
            <div class="label">⚠️ مراجعة</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_product_row(item, category="higher"):
    """عرض صف منتج"""
    diff = item.get("diff", 0)
    diff_class = "diff-higher" if diff > 0 else ("diff-lower" if diff < 0 else "diff-equal")
    priority = "priority-urgent" if abs(item.get("diff_pct", 0)) > 15 else (
        "priority-medium" if abs(item.get("diff_pct", 0)) > 5 else "priority-low"
    )

    return f"""
    <div class="product-row {priority}">
        <div class="name">
            <strong>{item.get('my_name', '')[:50]}</strong>
            <br><small style="color:#64748b">{item.get('comp_name', '')[:50]}</small>
        </div>
        <div style="text-align:center">
            <div class="price" style="color:#e2e8f0">{item.get('my_price', 0)}</div>
            <small style="color:#64748b">سعرك</small>
        </div>
        <div style="text-align:center">
            <div class="price" style="color:#94a3b8">{item.get('comp_price', 0)}</div>
            <small style="color:#64748b">المنافس</small>
        </div>
        <div class="diff {diff_class}">
            {'+' if diff > 0 else ''}{diff} ({'+' if item.get('diff_pct',0) > 0 else ''}{item.get('diff_pct', 0)}%)
        </div>
    </div>
    """


def _fmt(price):
    """تنسيق سعر مختصر"""
    if price is None or price == 0:
        return "—"
    try:
        p = float(price)
        return f"{int(p)}" if p == int(p) else f"{p:.1f}"
    except Exception:
        return str(price)


def render_product_card(product_name, my_price, competitors_prices,
                        product_no="", brand=""):
    """
    بطاقة منتج غنية — تعرض كل أسعار المنافسين بصرياً
    competitors_prices: {"comp_name": price, ...}
    """
    if not competitors_prices:
        return ""

    prices_list = list(competitors_prices.values())
    min_price = min(prices_list) if prices_list else 0
    max_price = max(prices_list) if prices_list else 0
    avg_price = sum(prices_list) / len(prices_list) if prices_list else 0
    all_prices = prices_list + ([my_price] if my_price else [])
    global_min = min(all_prices) if all_prices else 0
    global_max = max(all_prices) if all_prices else 1

    # Header
    no_badge = f'<span class="pcard-no">#{product_no}</span>' if product_no else ""
    brand_text = f'<div class="pcard-brand">{brand}</div>' if brand else ""

    html = f'''<div class="pcard">
    <div class="pcard-header">
        <div><div class="pcard-name">{product_name[:70]}</div>{brand_text}</div>
        {no_badge}
    </div>'''

    # My Price + diff from average
    diff_from_avg = my_price - avg_price if my_price and avg_price else 0
    diff_pct_avg = (diff_from_avg / avg_price * 100) if avg_price else 0
    diff_color = "#f87171" if diff_from_avg > 1 else ("#4ade80" if diff_from_avg < -1 else "#94a3b8")
    diff_text = f'+{diff_from_avg:.0f}' if diff_from_avg > 0 else f'{diff_from_avg:.0f}'

    html += f'''
    <div class="pcard-my-price">
        <span class="label">🏪 سعرك</span>
        <span class="value">{_fmt(my_price)}</span>
        <span class="sub" style="color:{diff_color}">{diff_text} عن المتوسط ({diff_pct_avg:+.1f}%)</span>
    </div>'''

    # Competitor Prices Grid
    html += '<div class="pcard-prices">'

    sorted_comps = sorted(competitors_prices.items(), key=lambda x: x[1])
    for comp_name, comp_price in sorted_comps:
        cls = ""
        if comp_price == min_price and len(prices_list) > 1:
            cls = "is-lowest"
        elif comp_price == max_price and len(prices_list) > 1 and max_price != min_price:
            cls = "is-highest"

        diff = my_price - comp_price if my_price else 0
        diff_pct = (diff / comp_price * 100) if comp_price else 0

        if diff > 1:
            diff_html = f'<div class="comp-diff" style="background:rgba(239,68,68,0.15);color:#f87171">+{diff:.0f} ({diff_pct:+.0f}%)</div>'
        elif diff < -1:
            diff_html = f'<div class="comp-diff" style="background:rgba(34,197,94,0.15);color:#4ade80">{diff:.0f} ({diff_pct:+.0f}%)</div>'
        else:
            diff_html = '<div class="comp-diff" style="background:rgba(148,163,184,0.12);color:#94a3b8">= نفسه</div>'

        html += f'''
        <div class="pcard-comp {cls}">
            <div class="comp-label">{comp_name[:15]}</div>
            <div class="comp-val">{_fmt(comp_price)}</div>
            {diff_html}
        </div>'''

    html += '</div>'

    # Visual Price Bar
    price_range = global_max - global_min if global_max != global_min else 1
    my_pos = ((my_price - global_min) / price_range * 100) if my_price else 50
    my_pos = max(2, min(98, my_pos))

    html += f'''
    <div class="price-bar-wrap">
        <div class="price-bar-labels">
            <span style="color:#4ade80">أقل: {_fmt(min_price)}</span>
            <span style="color:#a78bfa">سعرك: {_fmt(my_price)}</span>
            <span style="color:#f87171">أعلى: {_fmt(max_price)}</span>
        </div>
        <div class="price-bar-track">
            <div class="price-bar-fill" style="left:0; width:100%; background: linear-gradient(90deg, #22c55e, #fbbf24, #ef4444); opacity:0.25; border-radius:3px;"></div>
            <div style="position:absolute; top:-3px; right:{100-my_pos:.0f}%; width:12px; height:12px; background:#a78bfa; border-radius:50%; border:2px solid #1a1f2e; transform:translateX(50%);"></div>
        </div>
    </div>'''

    # Summary
    html += f'''
    <div class="pcard-summary">
        <div class="sum-item"><span class="sum-label">📊 متوسط:</span> <span class="sum-val blue">{_fmt(avg_price)}</span></div>
        <div class="sum-item"><span class="sum-label">📉 أقل:</span> <span class="sum-val green">{_fmt(min_price)}</span></div>
        <div class="sum-item"><span class="sum-label">📈 أعلى:</span> <span class="sum-val red">{_fmt(max_price)}</span></div>
        <div class="sum-item"><span class="sum-label">👥 منافسين:</span> <span class="sum-val purple">{len(competitors_prices)}</span></div>
    </div>'''

    # Recommendation
    if my_price and avg_price:
        if my_price > max_price:
            html += f'<div class="pcard-rec rec-lower">⚠️ سعرك أعلى من كل المنافسين بـ {_fmt(my_price - max_price)} — يُنصح بالخفض إلى {_fmt(avg_price * 0.98)}</div>'
        elif my_price > avg_price * 1.05:
            html += f'<div class="pcard-rec rec-lower">📉 سعرك أعلى من المتوسط بـ {diff_pct_avg:+.1f}% — خفض السعر لزيادة التنافسية</div>'
        elif my_price < min_price:
            html += f'<div class="pcard-rec rec-raise">💰 سعرك أقل من الكل! فرصة رفع حتى {_fmt(min_price)} (ربح +{_fmt(min_price - my_price)})</div>'
        elif my_price < avg_price * 0.95:
            html += '<div class="pcard-rec rec-raise">📈 سعرك أقل من المتوسط — يمكنك رفع السعر لزيادة الربح</div>'
        else:
            html += '<div class="pcard-rec rec-ok">✅ سعرك تنافسي ومناسب — لا تحتاج تعديل</div>'

    html += '</div>'
    return html
