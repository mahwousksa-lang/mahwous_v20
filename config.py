"""
إعدادات مهووس v20/v22 — نسخة كاملة
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
WEBHOOK_REPORT = os.environ.get("WEBHOOK_REPORT", "")

# ─────────────────────────────────────────────
# 🗄 قاعدة البيانات
# ─────────────────────────────────────────────
DB_PATH = "data/mahwous.db"

# ─────────────────────────────────────────────
# 📦 أعمدة الملفات (مطلوبة من helpers.py)
# ─────────────────────────────────────────────
PRODUCT_COLUMNS = [
    "product_no",
    "raw_name",
    "brand",
    "price",
]

PRICE_COLUMNS = [
    "raw_name",
    "price",
]

ID_COLUMNS = [
    "product_no",
]

BRAND_COLUMNS = [
    "brand",
]

# ─────────────────────────────────────────────
# 🧠 عتبات المطابقة
# ─────────────────────────────────────────────
MATCH_THRESHOLDS = {
    "exact": 0.90,
    "alias": 0.75,
    "review": 0.55,
    "reject": 0.40,
}

# ─────────────────────────────────────────────
# 🏷 مرادفات الماركات
# ─────────────────────────────────────────────
BRAND_SYNONYMS = {
    "dior": "Dior",
    "christian dior": "Dior",
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
    "edt": "Eau de Toilette",
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
