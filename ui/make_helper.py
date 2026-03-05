"""
utils/make_helper.py v23.0 — إرسال صحيح لـ Make.com
══════════════════════════════════════════════════════
Make Parameters (تحديث الأسعار):
  • product_id  — رقم المنتج في سلة
  • name        — اسم المنتج
  • price       — السعر الجديد

Make Parameters (منتجات جديدة/مفقودة):
  • أسم المنتج
  • سعر المنتج
  • الوصف
  • (حقول اختيارية أخرى)

⚠️ الإصلاح الحرج:
   تحديث الأسعار → كل منتج = طلب مستقل بـ payload مباشر (بدون wrapper)
   {product_id, name, price} وليس {products:[{...}]}
"""

import requests
import json
import os
import time
from typing import List, Dict, Any, Optional


# ── Webhook URLs ───────────────────────────────────────────────────────────
def _get_webhook_url(key: str, default: str) -> str:
    return os.environ.get(key, "") or default

WEBHOOK_UPDATE_PRICES = _get_webhook_url(
    "WEBHOOK_UPDATE_PRICES",
    "https://hook.eu2.make.com/8jia6gc7s1cpkeg6catlrvwck768sbfk"
)
WEBHOOK_NEW_PRODUCTS = _get_webhook_url(
    "WEBHOOK_NEW_PRODUCTS",
    "https://hook.eu2.make.com/xvubj23dmpxu8qzilstd25cnumrwtdxm"
)

TIMEOUT = 15  # ثانية


# ── الإرسال الأساسي ────────────────────────────────────────────────────────
def _post_to_webhook(url: str, payload: Any) -> Dict:
    if not url:
        return {"success": False, "message": "❌ Webhook URL غير محدد", "status_code": 0}
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        if resp.status_code in (200, 201, 202, 204):
            return {"success": True, "message": f"✅ ({resp.status_code})", "status_code": resp.status_code}
        return {"success": False, "message": f"❌ HTTP {resp.status_code}: {resp.text[:200]}", "status_code": resp.status_code}
    except requests.exceptions.Timeout:
        return {"success": False, "message": "❌ انتهت مهلة الاتصال", "status_code": 0}
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "❌ فشل الاتصال بـ Make", "status_code": 0}
    except Exception as e:
        return {"success": False, "message": f"❌ خطأ: {str(e)}", "status_code": 0}


# ── تحويل float آمن ───────────────────────────────────────────────────────
def _safe_float(val, default: float = 0.0) -> float:
    try:
        if val is None or str(val).strip() in ("", "nan", "None", "NaN"):
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


# ── تنظيف product_id ──────────────────────────────────────────────────────
def _clean_pid(raw) -> str:
    """
    product_id دائماً كـ str(int(float(value)))
    مثال: 100.0 → "100" | "1081786650.0" → "1081786650"
    """
    if raw is None: return ""
    s = str(raw).strip()
    if s in ("", "nan", "None", "NaN", "0", "0.0"): return ""
    try:
        # str(int(float(...))) يضمن 100.0 → "100"
        return str(int(float(s)))
    except (ValueError, TypeError):
        return s


# ══════════════════════════════════════════════════════════════════════════
#  إرسال منتج واحد — تحديث السعر
#  Payload: {"product_id": "...", "name": "...", "price": ...}
# ══════════════════════════════════════════════════════════════════════════
def send_single_product(product: Dict) -> Dict:
    """
    إرسال منتج واحد لتحديث سعره في سلة عبر Make.
    Make Parameters: product_id | name | price
    """
    name       = str(product.get("name", "")).strip()
    price      = _safe_float(product.get("price", 0))
    product_id = _clean_pid(product.get("product_id", ""))

    if not name:
        return {"success": False, "message": "❌ اسم المنتج مطلوب"}
    if price <= 0:
        return {"success": False, "message": f"❌ السعر غير صحيح: {price}"}

    # ── Payload مطابق لـ Make Parameters تماماً ──────────────────────────
    payload = {
        "product_id": product_id,
        "name":       name,
        "price":      price,
    }

    result = _post_to_webhook(WEBHOOK_UPDATE_PRICES, payload)
    if result["success"]:
        pid_info = f" [ID: {product_id}]" if product_id else ""
        result["message"] = f"✅ تم تحديث «{name}»{pid_info} ← {price:,.0f} ر.س"
    return result


# ══════════════════════════════════════════════════════════════════════════
#  إرسال عدة منتجات — تحديث الأسعار (كل منتج = طلب مستقل)
# ══════════════════════════════════════════════════════════════════════════
def send_price_updates(products: List[Dict]) -> Dict:
    """
    إرسال قائمة منتجات لتحديث أسعارها — كل منتج في طلب مستقل.
    Payload لكل طلب: {"product_id": "...", "name": "...", "price": ...}
    """
    if not products:
        return {"success": False, "message": "❌ لا توجد منتجات للإرسال"}

    sent, skipped, errors = 0, 0, []

    for p in products:
        name       = str(p.get("name", "")).strip()
        price      = _safe_float(p.get("price", 0))
        product_id = _clean_pid(p.get("product_id", ""))

        if not name or price <= 0:
            skipped += 1
            continue

        payload = {
            "product_id": product_id,          # str(int(float(...)))
            "name":       name,
            "price":      float(price),         # ← float صريح دائماً
        }

        result = _post_to_webhook(WEBHOOK_UPDATE_PRICES, payload)
        if result["success"]:
            sent += 1
        else:
            errors.append(f"{name}: {result['message']}")

        # تأخير بسيط بين الطلبات لتجنب Rate Limiting
        if len(products) > 1:
            time.sleep(0.3)

    if sent == 0:
        err_detail = " | ".join(errors[:3])
        return {"success": False, "message": f"❌ فشل إرسال جميع المنتجات. {err_detail}"}

    parts = [f"✅ تم تحديث {sent} منتج في Make"]
    if skipped: parts.append(f"تخطي {skipped}")
    if errors:  parts.append(f"فشل {len(errors)}")
    return {"success": True, "message": " | ".join(parts)}


# ══════════════════════════════════════════════════════════════════════════
#  تحويل DataFrame → قائمة منتجات مع حساب السعر الصحيح لكل قسم
# ══════════════════════════════════════════════════════════════════════════
def export_to_make_format(df, section_type: str = "update") -> List[Dict]:
    """
    تحويل DataFrame إلى قائمة منتجات جاهزة لـ Make.
    section_type: raise | lower | approved | update | missing | new
    """
    if df is None or (hasattr(df, "empty") and df.empty):
        return []

    products = []
    for _, row in df.iterrows():

        # ── رقم المنتج ────────────────────────────────────────────────────
        product_id = _clean_pid(
            row.get("معرف_المنتج")  or row.get("product_id")     or
            row.get("رقم المنتج")   or row.get("رقم_المنتج")    or
            row.get("معرف المنتج")  or row.get("sku")            or
            row.get("SKU")          or ""
        )

        # ── اسم المنتج ────────────────────────────────────────────────────
        name = (
            str(row.get("المنتج",         "")) or
            str(row.get("منتج_المنافس",   "")) or
            str(row.get("أسم المنتج",     "")) or
            str(row.get("اسم المنتج",     "")) or
            str(row.get("name",           "")) or ""
        ).strip()
        if name in ("", "nan", "None"): name = ""

        # ── السعر حسب القسم ───────────────────────────────────────────────
        comp_price = _safe_float(row.get("سعر_المنافس", 0))
        our_price  = _safe_float(
            row.get("السعر", 0) or row.get("سعر المنتج", 0) or
            row.get("price",  0) or 0
        )

        if section_type == "raise":
            # سعرنا أعلى → نُخفّض لسعر المنافس مطروحاً ريال
            price = round(comp_price - 1, 2) if comp_price > 0 else our_price
        elif section_type == "lower":
            # سعرنا أقل → نرفع لسعر المنافس مطروحاً ريال (نبقى أقل بريال)
            price = round(comp_price - 1, 2) if comp_price > 0 else our_price
        elif section_type in ("approved", "update"):
            price = our_price
        else:
            # missing / new: سعر المنافس
            price = comp_price if comp_price > 0 else our_price

        if not name: continue

        products.append({
            "product_id": product_id,
            "name":       name,
            "price":      price,
            # حقول سياقية (لا تُرسل لـ Make لكن مفيدة للـ debugging)
            "_section":   section_type,
            "_comp_price": comp_price,
            "_our_price":  our_price,
            "_brand":      str(row.get("الماركة", "")),
            "_competitor": str(row.get("المنافس", "")),
        })

    return products


# ══════════════════════════════════════════════════════════════════════════
#  إرسال منتجات جديدة / مفقودة — Webhook منفصل
#  Payload: {"data": [{"أسم المنتج":"...","سعر المنتج":...,"الوصف":"..."}]}
# ══════════════════════════════════════════════════════════════════════════
def send_new_products(products: List[Dict]) -> Dict:
    """إرسال منتجات جديدة لإضافتها في سلة عبر Make."""
    if not products:
        return {"success": False, "message": "❌ لا توجد منتجات للإرسال"}

    sent, skipped, errors = 0, 0, []

    for p in products:
        name  = str(p.get("name", p.get("أسم المنتج", ""))).strip()
        price = _safe_float(p.get("price", 0) or p.get("سعر المنتج", 0) or p.get("السعر", 0))

        if not name:
            skipped += 1
            continue

        item = {
            "أسم المنتج":      name,
            "سعر المنتج":      float(price),        # ← float صريح لـ Make/سلة
            "رمز المنتج sku":  "",
            "الوزن":           1,
            "سعر التكلفة":     float(_safe_float(p.get("cost_price", 0))),
            "السعر المخفض":    float(_safe_float(p.get("sale_price",  0))),
            "الوصف":           str(p.get("الوصف", p.get("description", ""))).strip(),
        }
        # حقل صورة اختياري
        if p.get("image_url"):
            item["صورة المنتج"] = str(p["image_url"])

        result = _post_to_webhook(WEBHOOK_NEW_PRODUCTS, {"data": [item]})
        if result["success"]:
            sent += 1
        else:
            errors.append(name)

        if len(products) > 1:
            time.sleep(0.3)

    if sent == 0:
        return {"success": False, "message": f"❌ فشل إرسال جميع المنتجات (تخطي {skipped})"}

    parts = [f"✅ تم إرسال {sent} منتج جديد إلى Make"]
    if skipped: parts.append(f"تخطي {skipped}")
    if errors:  parts.append(f"فشل {len(errors)}")
    return {"success": True, "message": " | ".join(parts)}


# ══════════════════════════════════════════════════════════════════════════
#  إرسال المنتجات المفقودة
# ══════════════════════════════════════════════════════════════════════════
def send_missing_products(products: List[Dict]) -> Dict:
    """إرسال المنتجات المفقودة لإضافتها في سلة عبر Make."""
    if not products:
        return {"success": False, "message": "❌ لا توجد منتجات مفقودة"}

    sent, skipped, errors = 0, 0, []

    for p in products:
        name  = str(p.get("name", p.get("المنتج", p.get("منتج_المنافس", "")))).strip()
        price = _safe_float(p.get("price", 0) or p.get("السعر", 0) or p.get("سعر_المنافس", 0))

        if not name:
            skipped += 1
            continue

        item = {
            "أسم المنتج":      name,
            "سعر المنتج":      float(price),        # ← float صريح لـ Make/سلة
            "رمز المنتج sku":  "",
            "الوزن":           1,
            "سعر التكلفة":     float(_safe_float(p.get("cost_price", 0))),
            "السعر المخفض":    float(_safe_float(p.get("sale_price",  0))),
            "الوصف":           str(p.get("الوصف", p.get("description", ""))).strip(),
        }
        if p.get("image_url"):
            item["صورة المنتج"] = str(p["image_url"])

        result = _post_to_webhook(WEBHOOK_NEW_PRODUCTS, {"data": [item]})
        if result["success"]:
            sent += 1
        else:
            errors.append(name)

        if len(products) > 1:
            time.sleep(0.3)

    if sent == 0:
        return {"success": False, "message": f"❌ فشل الإرسال (تخطي {skipped})"}

    parts = [f"✅ تم إرسال {sent} منتج مفقود إلى Make"]
    if skipped: parts.append(f"تخطي {skipped}")
    if errors:  parts.append(f"فشل {len(errors)}")
    return {"success": True, "message": " | ".join(parts)}


# ══════════════════════════════════════════════════════════════════════════
#  فحص الاتصال
# ══════════════════════════════════════════════════════════════════════════
def verify_webhook_connection() -> Dict:
    """فحص حالة الاتصال بـ Webhooks."""

    # فحص تحديث الأسعار — Payload المطابق للـ Parameters
    r1 = _post_to_webhook(WEBHOOK_UPDATE_PRICES, {
        "product_id": "test-001",
        "name":       "اختبار الاتصال",
        "price":      1.0,
    })

    # فحص المنتجات الجديدة
    r2 = _post_to_webhook(WEBHOOK_NEW_PRODUCTS, {
        "data": [{"أسم المنتج": "اختبار", "سعر المنتج": 1.0, "الوصف": "test"}]
    })

    return {
        "update_prices": {
            "success": r1["success"],
            "message": r1["message"],
            "url":     WEBHOOK_UPDATE_PRICES[:55] + "..." if len(WEBHOOK_UPDATE_PRICES) > 55 else WEBHOOK_UPDATE_PRICES,
        },
        "new_products": {
            "success": r2["success"],
            "message": r2["message"],
            "url":     WEBHOOK_NEW_PRODUCTS[:55] + "..." if len(WEBHOOK_NEW_PRODUCTS) > 55 else WEBHOOK_NEW_PRODUCTS,
        },
        "all_connected": r1["success"] and r2["success"],
    }
