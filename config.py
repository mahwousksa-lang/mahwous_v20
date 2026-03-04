"""
مهووس v22 — الإعدادات المركزية
نسخة نظيفة تشمل:
- إعدادات v20 الأصلية
- دعم محرك المطابقة Hybrid Arabic‑BERT
- عتبات مطابقة محسّنة
- مرادفات الماركات والتركيز
- إعدادات Make.com
- إعدادات قاعدة البيانات
"""

import os

# ─────────────────────────────────────────────
# 🔑 مفاتيح API
# ─────────────────────────────────────────────
GEMINI_API_KEYS = os.environ.get("GEMINI_API_KEYS", "[]")

# ─────────────────────────────────────────────
# 🌐 Webhooks (Make.com)
# ─────────────────────────────────────────────
WEBHOOK_UPDATE_PRICES = os.environ.get("WEBHOOK_UPDATE_PRICES", "")
WEBHOOK_NEW_PRODUCTS = os.environ.get("WEBHOOK_NEW_PRODUCTS", "")

# ─────────────────────────────────────────────
# 🗄 قاعدة البيانات
# ─────────────────────────────────────────────
DB_PATH = "data/mahwous.db"

# ─────────────────────────────────────────────
# 🧠 عتبات المطابقة (Hybrid Arabic‑BERT)
# ─────────────────────────────────────────────
MATCH_THRESHOLDS = {
    "exact": 0.90,     # مطابق تمامًا
    "alias": 0.75,     # موجود باسم مختلف
    "review": 0.55,    # يحتاج مراجعة
    "none": 0.00       # لا تطابق
}

# ─────────────────────────────────────────────
# 🧪 عتبات حسب الفئة (للعطور)
# ─────────────────────────────────────────────
CATEGORY_THRESHOLDS = {
    "perfume_famous": {"exact": 0.92, "medium": 0.75},
    "perfume_niche": {"exact": 0.85, "medium": 0.65},
    "oud_bakhoor": {"exact": 0.80, "medium": 0.60},
    "default": {"exact": 0.90, "medium": 0.70},
}

# ─────────────────────────────────────────────
# 📄 أعمدة الملفات المقبولة
# ─────────────────────────────────────────────
PRODUCT_COLUMNS = [
    "المنتج", "Product", "product", "product_name",
    "اسم المنتج", "Name", "name"
]

PRICE_COLUMNS = [
    "السعر", "Price", "price", "سعر", "الثمن",
    "Unit Price", "unit_price"
]

ID_COLUMNS = [
    "no", "NO", "No", "ID", "id", "رقم",
    "SKU", "sku", "الرقم", "رقم المنتج"
]

BRAND_COLUMNS = ["الماركة", "Brand", "brand", "الشركة", "العلامة"]
SIZE_COLUMNS = ["الحجم", "Size", "size", "ML", "ml"]

# ─────────────────────────────────────────────
# 🏷 تصنيفات المطابقة
# ─────────────────────────────────────────────
MATCH_LABELS = {
    "exact_match": "✅ تطابق كامل",
    "alias": "🔄 موجود باسم مختلف",
    "review": "⚠️ يحتاج مراجعة",
    "no_match": "❌ لا تطابق",
}

# ─────────────────────────────────────────────
# 💰 تصنيفات السعر
# ─────────────────────────────────────────────
PRICE_LABELS = {
    "higher": "🔴 سعرك أعلى",
    "lower": "🟢 سعرك أقل",
    "equal": "✅ نفس السعر",
    "missing": "🔵 مفقود",
}

# ─────────────────────────────────────────────
# 🧴 مرادفات التركيز
# ─────────────────────────────────────────────
CONCENTRATION_SYNONYMS = {
    "edp": ["edp", "eau de parfum", "بارفيوم", "بارفان", "او دي بارفيوم", "parfum"],
    "edt": ["edt", "eau de toilette", "تواليت", "او دي تواليت", "toilette"],
    "edc": ["edc", "eau de cologne", "كولون", "او دي كولون", "cologne"],
    "parfum": ["parfum", "extrait", "بيور بارفيوم", "اكستريت", "pure parfum"],
    "body_mist": ["body mist", "بودي مست", "مست", "سبلاش", "splash"],
}

# ─────────────────────────────────────────────
# 🏭 مرادفات الماركات (عربي ↔ إنجليزي)
# ─────────────────────────────────────────────
BRAND_SYNONYMS = {
    "dior": ["ديور", "dior", "christian dior", "كريستيان ديور"],
    "chanel": ["شانيل", "chanel"],
    "versace": ["فرزاتشي", "فيرساتشي", "versace"],
    "gucci": ["قوتشي", "غوتشي", "gucci"],
    "armani": ["ارماني", "أرماني", "armani", "giorgio armani", "جورجيو ارماني"],
    "ysl": ["يسل", "واي اس ال", "ysl", "yves saint laurent", "ايف سان لوران"],
    "tom_ford": ["توم فورد", "tom ford"],
    "creed": ["كريد", "creed"],
    "lattafa": ["لطافة", "lattafa"],
    "rasasi": ["رصاصي", "rasasi"],
    "ajmal": ["أجمل", "اجمل", "ajmal"],
    "swiss_arabian": ["سويس اربيان", "swiss arabian"],
    "afnan": ["أفنان", "افنان", "afnan"],
    "prada": ["برادا", "prada"],
    "burberry": ["بربري", "burberry"],
    "dolce_gabbana": ["دولتشي اند غابانا", "دولتشي", "dolce & gabbana", "dolce gabbana", "d&g"],
    "hugo_boss": ["هوغو بوس", "hugo boss", "boss"],
    "calvin_klein": ["كالفن كلاين", "calvin klein", "ck"],
    "givenchy": ["جيفنشي", "givenchy"],
    "bvlgari": ["بولغاري", "بلغاري", "bvlgari", "bulgari"],
    "montblanc": ["مونت بلانك", "montblanc", "mont blanc"],
    "davidoff": ["دافيدوف", "davidoff"],
    "jimmy_choo": ["جيمي تشو", "jimmy choo"],
    "carolina_herrera": ["كارولينا هيريرا", "carolina herrera"],
    "narciso_rodriguez": ["نارسيسو رودريغز", "narciso rodriguez"],
    "lancome": ["لانكوم", "lancome"],
    "hermes": ["هيرميس", "hermes", "hermès"],
}

# ─────────────────────────────────────────────
# 🎨 ألوان الواجهة
# ─────────────────────────────────────────────
COLORS = {
    "primary": "#6C63FF",
    "success": "#00C853",
    "danger": "#FF5252",
    "warning": "#FFB300",
    "info": "#29B6F6",
    "dark": "#1A1F2E",
    "card": "#1E2436",
    "text": "#FAFAFA",
    "muted": "#8892A0",
    "border": "#2A3042",
}
