"""
مهووس v22 — إرسال البيانات للـ Webhooks (Make.com)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• إرسال تحديثات الأسعار
• إرسال المنتجات المفقودة
• إرسال تقرير كامل
• دعم retry تلقائي
"""

import json
import time
from datetime import datetime

try:
    import urllib.request
    URLLIB_AVAILABLE = True
except ImportError:
    URLLIB_AVAILABLE = False


def _send_webhook(url: str, payload: dict, retries: int = 2):
    if not url or not URLLIB_AVAILABLE:
        return False, "❌ لا يوجد Webhook URL"

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                status = resp.getcode()
                if 200 <= status < 300:
                    return True, f"تم الإرسال (HTTP {status})"
                return False, f"HTTP {status}"
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
            else:
                return False, f"خطأ: {str(e)[:80]}"

    return False, "فشل بعد كل المحاولات"


def send_price_updates(webhook_url: str, items: list, session_id: str = ""):
    if not items:
        return {"success": False, "message": "لا توجد عناصر"}

    payload = {
        "event": "price_updates",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "total": len(items),
        "items": [
            {
                "product_no": str(i.get("product_no", "")),
                "product_name": str(i.get("my_name", ""))[:80],
                "current_price": float(i.get("my_price", 0)),
                "suggested_price": float(i.get("comp_price", i.get("my_price", 0))),
                "competitor": str(i.get("competitor", "")),
                "competitor_price": float(i.get("comp_price", 0)),
                "diff_pct": float(i.get("diff_pct", 0)),
            }
            for i in items[:200]
        ]
    }

    ok, msg = _send_webhook(webhook_url, payload)
    return {"success": ok, "message": msg, "count": len(items)}


def send_missing_products(webhook_url: str, items: list, session_id: str = ""):
    if not items:
        return {"success": False, "message": "لا توجد منتجات مفقودة"}

    payload = {
        "event": "missing_products",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "total": len(items),
        "items": [
            {
                "product_name": str(i.get("comp_name", ""))[:80],
                "brand": str(i.get("brand", "")),
                "competitor": str(i.get("competitor", "")),
                "competitor_price": float(i.get("comp_price", 0)),
                "importance": float(i.get("importance_score", 0)),
                "competitors_count": int(i.get("competitors_count", 1)),
            }
            for i in items[:200]
        ]
    }

    ok, msg = _send_webhook(webhook_url, payload)
    return {"success": ok, "message": msg, "count": len(items)}


def send_full_report(webhook_url: str, stats: dict, session_id: str = ""):
    payload = {
        "event": "analysis_complete",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
    }

    ok, msg = _send_webhook(webhook_url, payload)
    return {"success": ok, "message": msg}
