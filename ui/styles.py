import streamlit as st


def inject_css():
    css = """
    <style>
    /* خلفية الصفحة */
    .stApp {
        background-color: #050816;
        color: #ffffff;
    }

    /* إخفاء الهيدر والفوتر الافتراضيين */
    header, footer {visibility: hidden;}

    /* كروت الإحصائيات */
    .stat-card {
        background: #0f172a;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #1e293b;
    }
    .stat-title {
        font-size: 0.9rem;
        color: #9ca3af;
    }
    .stat-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e5e7eb;
    }

    /* كرت المنتج */
    .product-card {
        background: #020617;
        border-radius: 14px;
        padding: 16px 18px;
        border: 1px solid #1f2937;
        margin-bottom: 10px;
    }
    .product-title {
        font-weight: 700;
        font-size: 1rem;
        color: #e5e7eb;
    }
    .product-sub {
        font-size: 0.85rem;
        color: #9ca3af;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header():
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("### مهووس v22 — لوحة تحليل الأسعار الذكية")
        st.markdown("#### مقارنة أسعارك مع المنافسين + اكتشاف المنتجات الناقصة")
    with col2:
        st.markdown(
            "<div style='text-align:right; font-size:0.85rem; color:#9ca3af;'>إصدار v22</div>",
            unsafe_allow_html=True,
        )


def render_stats_cards(stats: dict):
    """
    stats مثال:
    {
        "total_my_products": 120,
        "total_matched": 80,
        "total_higher": 20,
        "total_lower": 30,
        "total_missing": 10,
    }
    """
    col1, col2, col3, col4, col5 = st.columns(5)

    def _card(col, title, value):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-title">{title}</div>
                    <div class="stat-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    _card(col1, "عدد منتجاتك", stats.get("total_my_products", 0))
    _card(col2, "تمت مطابقتها", stats.get("total_matched", 0))
    _card(col3, "أعلى من المنافس", stats.get("total_higher", 0))
    _card(col4, "أقل من المنافس", stats.get("total_lower", 0))
    _card(col5, "منتجات ناقصة", stats.get("total_missing", 0))


def render_product_card(product: dict):
    """
    product مثال:
    {
        "raw_name": "...",
        "brand": "...",
        "my_price": 100,
        "competitor_name": "...",
        "competitor_price": 120,
        "price_diff": -20,
        "price_status": "lower" / "higher" / "equal",
    }
    """
    diff = product.get("price_diff")
    status = product.get("price_status", "")
    color = "#22c55e" if status == "lower" else "#ef4444" if status == "higher" else "#e5e7eb"

    st.markdown(
        f"""
        <div class="product-card">
            <div class="product-title">{product.get("raw_name","")}</div>
            <div class="product-sub">{product.get("brand","")}</div>
            <div class="product-sub">
                سعرك: {product.get("my_price","-")} — منافس: {product.get("competitor_price","-")} ({product.get("competitor_name","")})
            </div>
            <div class="product-sub" style="color:{color};">
                فرق السعر: {diff}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
