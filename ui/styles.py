import streamlit as st

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
def inject_css():
    css = """
    <style>
    .stApp {
        background-color: #0F1117;
        color: #FAFAFA;
    }

    header, footer {visibility: hidden;}

    .stat-card {
        background: #1E2436;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2c3245;
    }
    .stat-title {
        font-size: 0.9rem;
        color: #9ca3af;
    }
    .stat-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
    }

    .product-card {
        background: #1A1F2E;
        border-radius: 14px;
        padding: 16px 18px;
        border: 1px solid #2c3245;
        margin-bottom: 10px;
    }
    .product-title {
        font-weight: 700;
        font-size: 1rem;
        color: #ffffff;
    }
    .product-sub {
        font-size: 0.85rem;
        color: #9ca3af;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER — متوافق مع app.py
# ─────────────────────────────────────────────
def render_header(ai_available=False, ai_calls=0):
    status_color = "#22c55e" if ai_available else "#ef4444"
    status_text = "متاح" if ai_available else "غير متاح"

    st.markdown(
        f"""
        <div style="padding: 15px 0 25px 0;">
            <h2 style="margin-bottom: 6px; color:#ffffff;">
                مهووس v22 — لوحة تحليل الأسعار الذكية
            </h2>

            <div style="font-size: 0.9rem; color:#9ca3af;">
                حالة الذكاء الاصطناعي:
                <span style="color:{status_color}; font-weight:700;">
                    {status_text}
                </span>
                — عدد النداءات: {ai_calls}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# STAT CARDS
# ─────────────────────────────────────────────
def render_stats_cards(stats: dict):
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


# ─────────────────────────────────────────────
# PRODUCT CARD
# ─────────────────────────────────────────────
def render_product_card(product: dict):
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
