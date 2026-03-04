"""
مهووس v21 — محرك المطابقة الذكي + طبقة AI اختيارية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• تفكيك المنتج لحقول ذكية (ماركة، اسم، تركيز، حجم)
• بصمة فريدة لمنع التكرار
• مطابقة متعددة الطبقات
• تصنيف 5 مستويات
• قاموس مرادفات عربي ↔ إنجليزي
• طبقة رابعة اختيارية بالذكاء الاصطناعي (Gemini) للحالات الغامضة
"""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Callable, Any

from config import CONCENTRATION_SYNONYMS, BRAND_SYNONYMS, MATCH_THRESHOLDS


# ═══════════════════════════════════════════════════
# SmartEngine الأساسي
# ═══════════════════════════════════════════════════
class SmartEngine:
    """محرك المطابقة الذكي v21 (بدون AI)"""

    def __init__(self, db=None):
        self.db = db
        self._build_lookup_tables()

    def _build_lookup_tables(self):
        """بناء جداول البحث السريع"""
        self.conc_lookup = {}
        for key, synonyms in CONCENTRATION_SYNONYMS.items():
            for syn in synonyms:
                self.conc_lookup[syn.lower().strip()] = key

        self.brand_lookup = {}
        for key, synonyms in BRAND_SYNONYMS.items():
            for syn in synonyms:
                self.brand_lookup[syn.lower().strip()] = key

    # ─────────────────────────────────────────────
    # 1) تفكيك المنتج
    # ─────────────────────────────────────────────
    def parse_product(self, raw_name: str) -> Dict[str, Any]:
        if not raw_name or not isinstance(raw_name, str):
            return {
                "brand": "",
                "name": str(raw_name or ""),
                "concentration": "",
                "size": None,
                "raw": str(raw_name or ""),
            }

        text = self._normalize(raw_name)
        result = {
            "brand": "",
            "name": "",
            "concentration": "",
            "size": None,
            "raw": raw_name.strip(),
        }

        # الحجم
        size_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:ml|مل|ملل|cc)',
            r'(\d+(?:\.\d+)?)\s*(?:g|جرام|غرام|gm|gram)',
        ]
        for pattern in size_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                result["size"] = float(m.group(1))
                text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
                break

        # التركيز
        conc_patterns = [
            r'\b(eau\s+de\s+parfum|eau\s+de\s+toilette|eau\s+de\s+cologne)\b',
            r'\b(edp|edt|edc|parfum|extrait|cologne|body\s+mist|بارفيوم|تواليت|كولون|بودي\s*مست)\b',
        ]
        for pattern in conc_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                found = m.group(1).lower().strip()
                result["concentration"] = self.conc_lookup.get(found, found)
                text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
                break

        # الماركة
        text_clean = re.sub(r'\s+', ' ', text).strip()
        text_lower = text_clean.lower()

        sorted_brands = sorted(self.brand_lookup.keys(), key=len, reverse=True)
        for brand_syn in sorted_brands:
            if brand_syn in text_lower:
                result["brand"] = self.brand_lookup[brand_syn]
                idx = text_lower.find(brand_syn)
                text_clean = text_clean[:idx] + text_clean[idx + len(brand_syn):]
                text_lower = text_clean.lower()
                break

        if not result["brand"]:
            words = text_clean.split()
            if words:
                first = words[0].lower()
                result["brand"] = self.brand_lookup.get(first, first)
                text_clean = ' '.join(words[1:]) if len(words) > 1 else text_clean

        result["name"] = self._clean_name(text_clean)
        return result

    def _normalize(self, text: str) -> str:
        text = unicodedata.normalize("NFKC", str(text))
        text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670]', '', text)
        text = re.sub(r'[إأآا]', 'ا', text)
        text = re.sub(r'ة', 'ه', text)
        text = re.sub(r'ى', 'ي', text)
        text = re.sub(r'[^\w\s\u0600-\u06FF&\-.]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _clean_name(self, text: str) -> str:
        stopwords = {
            'for', 'men', 'women', 'homme', 'femme', 'pour', 'by', 'de', 'la', 'le',
            'the', 'and', 'with', 'new', 'set', 'gift',
            'عطر', 'من', 'الى', 'مع', 'في', 'على', 'رجالي', 'نسائي', 'للرجال', 'للنساء',
        }
        words = text.split()
        cleaned = [w for w in words if w.lower() not in stopwords and len(w) > 1]
        return ' '.join(cleaned).strip()

    # ─────────────────────────────────────────────
    # 2) البصمة
    # ─────────────────────────────────────────────
    def fingerprint(self, raw_name: str, brand_hint: Optional[str] = None) -> str:
        parsed = self.parse_product(raw_name)
        brand = parsed["brand"] or (brand_hint.lower() if brand_hint else "")
        name = re.sub(r'[^a-z0-9\u0600-\u06FF]', '', parsed["name"].lower())
        conc = parsed["concentration"] or ""
        size = str(int(parsed["size"])) if parsed["size"] else ""

        fp = f"{brand}_{name}_{conc}_{size}".strip("_")
        fp = re.sub(r'_+', '_', fp)
        return fp if len(fp) > 3 else self._fallback_fingerprint(raw_name)

    def _fallback_fingerprint(self, raw_name: str) -> str:
        text = self._normalize(str(raw_name).lower())
        text = re.sub(r'[^a-z0-9\u0600-\u06FF]', '', text)
        return f"raw_{text[:60]}"

    # ─────────────────────────────────────────────
    # 3) المطابقة
    # ─────────────────────────────────────────────
    def _name_similarity(self, a: str, b: str) -> float:
        if not a or not b:
            return 0
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _field_match(self, p1, p2):
        score = 0

        # الماركة (30%)
        brand_score = 0
        if p1["brand"] and p2["brand"]:
            if p1["brand"] == p2["brand"]:
                brand_score = 100
            elif self._name_similarity(p1["brand"], p2["brand"]) > 0.7:
                brand_score = 80
        elif not p1["brand"] and not p2["brand"]:
            brand_score = 50
        score += brand_score * 0.30

        # الاسم (40%)
        name_score = self._name_similarity(p1["name"], p2["name"]) * 100
        score += name_score * 0.40

        # التركيز (15%)
        conc_score = 0
        if p1["concentration"] and p2["concentration"]:
            conc_score = 100 if p1["concentration"] == p2["concentration"] else 20
        elif not p1["concentration"] and not p2["concentration"]:
            conc_score = 70
        else:
            conc_score = 50
        score += conc_score * 0.15

        # الحجم (15%)
        size_score = 0
        if p1["size"] and p2["size"]:
            size_score = 100 if p1["size"] == p2["size"] else 40
        elif not p1["size"] and not p2["size"]:
            size_score = 60
        else:
            size_score = 40
        score += size_score * 0.15

        return score

    def match(self, my_product: str, competitor_product: str) -> Dict[str, Any]:
        p1 = self.parse_product(my_product)
        p2 = self.parse_product(competitor_product)

        fp1 = self.fingerprint(my_product)
        fp2 = self.fingerprint(competitor_product)

        # بصمة
        if fp1 == fp2:
            return {"confidence": 100, "match_type": "exact_match", "details": "تطابق كامل بالبصمة"}

        # alias
        if self.db:
            alias_match = self.db.find_by_alias(competitor_product.strip().lower())
            if alias_match and alias_match["fingerprint"] == fp1:
                return {"confidence": 99, "match_type": "exact_match", "details": "تطابق عبر الأسماء البديلة"}

        # الحقول الذكية
        score = self._field_match(p1, p2)

        if score >= MATCH_THRESHOLDS["exact"]:
            match_type = "exact_match"
        elif score >= MATCH_THRESHOLDS["high"]:
            match_type = "exact_match"
        elif score >= MATCH_THRESHOLDS["medium"]:
            match_type = "review"
        elif score >= MATCH_THRESHOLDS["low"]:
            match_type = "review"
        else:
            match_type = "no_match"

        return {
            "confidence": round(score, 1),
            "match_type": match_type,
            "details": f"{p1} ↔ {p2}",
        }

    # ─────────────────────────────────────────────
    # 4) تحليل كامل
    # ─────────────────────────────────────────────
    def analyze(self, my_products, competitor_products, competitor_name,
                session_id=None, progress_callback=None):

        results = {
            "higher": [],
            "lower": [],
            "equal": [],
            "review": [],
            "missing": [],
            "price_changes": [],
            "stats": {},
        }

        # فهرس منتجاتي
        my_index = self.db.get_all_my_fingerprints() if self.db else {}

        total = len(competitor_products) or 1

        for idx, comp in enumerate(competitor_products, start=1):
            comp_name = comp.get("name", "")
            comp_price = float(comp.get("price", 0) or 0)
            comp_fp = self.fingerprint(comp_name)

            best_match = None
            best_score = 0
            best_fp = None

            for fp, my_p in my_index.items():
                m = self.match(my_p.get("raw_name", my_p.get("name", "")), comp_name)
                score = m.get("confidence", 0)
                if score > best_score:
                    best_score = score
                    best_match = my_p
                    best_fp = fp

            # مطابق
            if best_match and best_score >= MATCH_THRESHOLDS["medium"]:
                my_price = float(best_match.get("current_price", 0))
                diff = round(my_price - comp_price, 2)
                diff_pct = round((diff / comp_price * 100), 1) if comp_price else 0

                results["equal"].append({
                    "my_name": best_match.get("raw_name", ""),
                    "my_price": my_price,
                    "comp_name": comp_name,
                    "comp_price": comp_price,
                    "diff": diff,
                    "diff_pct": diff_pct,
                    "confidence": best_score,
                    "competitor": competitor_name,
                    "fingerprint": best_fp,
                })

            else:
                # مفقود
                parsed = self.parse_product(comp_name)
                results["missing"].append({
                    "comp_name": comp_name,
                    "comp_price": comp_price,
                    "competitor": competitor_name,
                    "brand": parsed["brand"],
                    "best_score": best_score,
                    "fingerprint": comp_fp,
                })

            if progress_callback:
                progress_callback(idx / total, f"تحليل {idx}/{total}")

        return results


# ═══════════════════════════════════════════════════
# SmartEngineV21 — مع AI
# ═══════════════════════════════════════════════════
class SmartEngineV21(SmartEngine):
    def __init__(self, db=None, ai_engine=None):
        super().__init__(db=db)
        self.ai = ai_engine

    def match(self, my_product, competitor_product):
        base = super().match(my_product, competitor_product)
        conf = base["confidence"]

        if conf >= 85 or conf < 50:
            return base

        if self.ai and self.ai.available:
            ai_result = self.ai.match_products(my_product, competitor_product)
            if ai_result.get("is_same") is not None:
                ai_conf = ai_result.get("confidence", conf)
                blended = round(ai_conf * 0.6 + conf * 0.4, 1)

                if ai_result["is_same"] and blended >= 70:
                    match_type = "exact_match"
                elif not ai_result["is_same"]:
                    match_type = "no_match"
                    blended = min(blended, 49)
                else:
                    match_type = "review"

                return {
                    "confidence": blended,
                    "match_type": match_type,
                    "details": f"AI: {ai_result.get('reason','')} | {base['details']}",
                    "ai_used": True,
                }

        return base


# ═══════════════════════════════════════════════════
# دالة run_full_analysis — المطلوبة لـ app.py
# ═══════════════════════════════════════════════════
def run_full_analysis(my_products, competitor_products, competitor_name,
                      db=None, ai=None, session_id=None, progress_callback=None):

    engine = SmartEngineV21(db=db, ai_engine=ai) if ai else SmartEngine(db=db)

    return engine.analyze(
        my_products=my_products,
        competitor_products=competitor_products,
        competitor_name=competitor_name,
        session_id=session_id,
        progress_callback=progress_callback
    )
