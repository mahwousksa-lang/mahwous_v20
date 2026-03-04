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
    "reject": 0.40     # مرفوض
}

# ─────────────────────────────────────────────
# 🏷 مرادفات الماركات
# ─────────────────────────────────────────────
BRAND_SYNONYMS = {
    "dior": "Dior",
    "christian dior": "Dior",
    "dior perfumes": "Dior",
    "ysl": "Yves Saint Laurent",
    "yves saint laurent": "Yves Saint Laurent",
    "armani": "Giorgio Armani",
    "giorgio armani": "Giorgio Armani",
}

# ─────────────────────────────────────────────
# 🧪 مرادفات التركيز
# ─────────────────────────────────────────────
CONCENTRATION_SYNONYMS = {
    "edp": "Eau de Parfum",
    "eau de parfum": "Eau de Parfum",
    "edt": "Eau de Toilette",
    "eau de toilette": "Eau de Toilette",
    "parfum": "Parfum",
}

# ─────────────────────────────────────────────
# 📦 إعدادات الملفات
# ─────────────────────────────────────────────
MAX_UPLOAD_MB = 50
ALLOWED_EXTENSIONS = ["xlsx", "xls", "csv"]

# ─────────────────────────────────────────────
# 🛒 المنافسون
# ─────────────────────────────────────────────
COMPETITORS = [
    "NiceOne",
    "GoldenScent",
    "Faces",
    "Boutiqaat",
    "Amazon",
]
