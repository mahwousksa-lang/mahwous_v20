"""
مهووس v20 — محرك المطابقة الذكي
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• تفكيك المنتج لحقول ذكية (ماركة، اسم، تركيز، حجم)
• بصمة فريدة لمنع التكرار
• مطابقة متعددة الطبقات
• تصنيف 5 مستويات
• قاموس مرادفات عربي ↔ إنجليزي
"""
import re
import unicodedata
from difflib import SequenceMatcher
from config import CONCENTRATION_SYNONYMS, BRAND_SYNONYMS, MATCH_THRESHOLDS


class SmartEngine:
    """محرك المطابقة الذكي v20"""

    def __init__(self, db=None):
        self.db = db
        self._build_lookup_tables()

    def _build_lookup_tables(self):
        """بناء جداول البحث السريع"""
        # ─── جدول التركيز ───
        self.conc_lookup = {}
        for key, synonyms in CONCENTRATION_SYNONYMS.items():
            for syn in synonyms:
                self.conc_lookup[syn.lower().strip()] = key

        # ─── جدول الماركات ───
        self.brand_lookup = {}
        for key, synonyms in BRAND_SYNONYMS.items():
            for syn in synonyms:
                self.brand_lookup[syn.lower().strip()] = key

    # ═══════════════════════════════════════════════════
    # 1. تفكيك المنتج (Smart Parsing)
    # ═══════════════════════════════════════════════════
    def parse_product(self, raw_name):
        """
        تفكيك اسم المنتج إلى حقول ذكية
        مثال: "Dior Sauvage EDP 100ml" →
        {brand: "dior", name: "sauvage", concentration: "edp", size: 100}
        """
        if not raw_name or not isinstance(raw_name, str):
            return {"brand": "", "name": str(raw_name or ""), "concentration": "", "size": None, "raw": str(raw_name or "")}

        text = self._normalize(raw_name)
        result = {
            "brand": "",
            "name": "",
            "concentration": "",
            "size": None,
            "raw": raw_name.strip(),
        }

        # ─── استخراج الحجم ───
        size_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:ml|مل|ملل|cc)',
            r'(\d+(?:\.\d+)?)\s*(?:g|جرام|غرام|gm|gram)',
        ]
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["size"] = float(match.group(1))
                text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
                break

        # ─── استخراج التركيز ───
        conc_patterns = [
            r'\b(eau\s+de\s+parfum|eau\s+de\s+toilette|eau\s+de\s+cologne)\b',
            r'\b(edp|edt|edc|parfum|extrait|cologne|body\s+mist|بارفيوم|تواليت|كولون|بودي\s*مست)\b',
        ]
        for pattern in conc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found = match.group(1).lower().strip()
                result["concentration"] = self.conc_lookup.get(found, found)
                text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
                break

        # ─── استخراج الماركة ───
        text_clean = re.sub(r'\s+', ' ', text).strip()
        text_lower = text_clean.lower()

        # ترتيب الماركات بالأطول أولاً لتجنب المطابقة الجزئية
        sorted_brands = sorted(self.brand_lookup.keys(), key=len, reverse=True)
        for brand_syn in sorted_brands:
            if brand_syn in text_lower:
                result["brand"] = self.brand_lookup[brand_syn]
                # إزالة الماركة من النص
                idx = text_lower.find(brand_syn)
                text_clean = text_clean[:idx] + text_clean[idx + len(brand_syn):]
                text_lower = text_clean.lower()
                break

        # إذا لم نجد ماركة، أول كلمة تكون الماركة
        if not result["brand"]:
            words = text_clean.split()
            if words:
                first = words[0].lower()
                result["brand"] = self.brand_lookup.get(first, first)
                text_clean = ' '.join(words[1:]) if len(words) > 1 else text_clean

        # ─── الاسم المتبقي ───
        result["name"] = self._clean_name(text_clean)

        return result

    def _normalize(self, text):
        """تطبيع النص"""
        if not text:
            return ""
        text = str(text)
        # توحيد Unicode
        text = unicodedata.normalize("NFKC", text)
        # إزالة التشكيل العربي
        text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670]', '', text)
        # توحيد الألفات
        text = re.sub(r'[إأآا]', 'ا', text)
        text = re.sub(r'ة', 'ه', text)
        text = re.sub(r'ى', 'ي', text)
        # إزالة الرموز الخاصة (مع الإبقاء على & و -)
        text = re.sub(r'[^\w\s\u0600-\u06FF&\-.]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _clean_name(self, text):
        """تنظيف الاسم من الكلمات الفارغة"""
        stopwords = {
            'for', 'men', 'women', 'homme', 'femme', 'pour', 'by', 'de', 'la', 'le',
            'the', 'and', 'with', 'new', 'set', 'gift',
            'عطر', 'من', 'الى', 'مع', 'في', 'على', 'رجالي', 'نسائي', 'للرجال', 'للنساء',
        }
        words = text.split()
        cleaned = [w for w in words if w.lower() not in stopwords and len(w) > 1]
        return ' '.join(cleaned).strip()

    # ═══════════════════════════════════════════════════
    # 2. البصمة الفريدة (Fingerprint)
    # ═══════════════════════════════════════════════════
    def fingerprint(self, raw_name, brand_hint=None):
        """
        إنشاء بصمة فريدة للمنتج — أساس منع التكرار
        البصمة = ماركة_اسم_تركيز_حجم
        """
        parsed = self.parse_product(raw_name)
        brand = parsed["brand"] or (brand_hint.lower() if brand_hint else "")
        name = re.sub(r'[^a-z0-9\u0600-\u06FF]', '', parsed["name"].lower())
        conc = parsed["concentration"] or ""
        size = str(int(parsed["size"])) if parsed["size"] else ""

        fp = f"{brand}_{name}_{conc}_{size}".strip("_")
        # تنظيف نهائي
        fp = re.sub(r'_+', '_', fp)
        return fp if len(fp) > 3 else self._fallback_fingerprint(raw_name)

    def _fallback_fingerprint(self, raw_name):
        """بصمة احتياطية للأسماء التي لا يمكن تفكيكها"""
        text = self._normalize(str(raw_name).lower())
        text = re.sub(r'[^a-z0-9\u0600-\u06FF]', '', text)
        return f"raw_{text[:60]}"

    # ═══════════════════════════════════════════════════
    # 3. المطابقة متعددة الطبقات
    # ═══════════════════════════════════════════════════
    def match(self, my_product, competitor_product):
        """
        مطابقة منتج من مهووس مع منتج منافس
        يرجع: {confidence, match_type, details}
        """
        p1 = self.parse_product(my_product)
        p2 = self.parse_product(competitor_product)

        # ─── الطبقة 1: مطابقة البصمة (100%) ───
        fp1 = self.fingerprint(my_product)
        fp2 = self.fingerprint(competitor_product)
        if fp1 == fp2:
            return {"confidence": 100, "match_type": "exact_match", "details": "تطابق كامل بالبصمة"}

        # ─── الطبقة 2: الأسماء البديلة في قاعدة البيانات ───
        if self.db:
            alias_match = self.db.find_by_alias(competitor_product.strip().lower())
            if alias_match and alias_match["fingerprint"] == fp1:
                return {"confidence": 99, "match_type": "exact_match", "details": "تطابق عبر الأسماء البديلة"}

        # ─── الطبقة 3: مطابقة بالحقول الذكية ───
        score = self._field_match(p1, p2)

        # ─── تحديد النوع ───
        match_type = "no_match"
        if score >= MATCH_THRESHOLDS["exact"]:
            match_type = "exact_match"
        elif score >= MATCH_THRESHOLDS["high"]:
            # تحقق: هل الفرق فقط في الحجم أو التركيز؟
            if p1["brand"] == p2["brand"] and self._name_similarity(p1["name"], p2["name"]) > 0.8:
                if p1["size"] and p2["size"] and p1["size"] != p2["size"]:
                    match_type = "size_diff"
                elif p1["concentration"] and p2["concentration"] and p1["concentration"] != p2["concentration"]:
                    match_type = "conc_diff"
                else:
                    match_type = "exact_match"
            else:
                match_type = "exact_match"
        elif score >= MATCH_THRESHOLDS["medium"]:
            match_type = "review"
        elif score >= MATCH_THRESHOLDS["low"]:
            match_type = "review"
        else:
            match_type = "no_match"

        details = self._build_details(p1, p2, score)

        return {"confidence": round(score, 1), "match_type": match_type, "details": details}

    def _field_match(self, p1, p2):
        """مطابقة بالحقول مع أوزان"""
        score = 0

        # الماركة (30%)
        brand_score = 0
        if p1["brand"] and p2["brand"]:
            if p1["brand"] == p2["brand"]:
                brand_score = 100
            elif self._name_similarity(p1["brand"], p2["brand"]) > 0.7:
                brand_score = 80
        elif not p1["brand"] and not p2["brand"]:
            brand_score = 50  # كلاهما بدون ماركة
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
            size_score = 100 if p1["size"] == p2["size"] else 20
        elif not p1["size"] and not p2["size"]:
            size_score = 70
        else:
            size_score = 50
        score += size_score * 0.15

        return min(100, score)

    def _name_similarity(self, name1, name2):
        """حساب تشابه الأسماء"""
        if not name1 or not name2:
            return 0
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        if n1 == n2:
            return 1.0

        # Sequence matcher
        ratio = SequenceMatcher(None, n1, n2).ratio()

        # Token-based: تشابه الكلمات
        words1 = set(n1.split())
        words2 = set(n2.split())
        if words1 and words2:
            common = words1 & words2
            token_ratio = len(common) / max(len(words1), len(words2))
            ratio = max(ratio, token_ratio)

        return ratio

    def _build_details(self, p1, p2, score):
        """بناء تفاصيل المطابقة"""
        parts = []
        if p1["brand"] == p2["brand"] and p1["brand"]:
            parts.append(f"✅ ماركة: {p1['brand']}")
        elif p1["brand"] or p2["brand"]:
            parts.append(f"⚠️ ماركة: {p1['brand']} ↔ {p2['brand']}")

        if p1["size"] and p2["size"]:
            if p1["size"] == p2["size"]:
                parts.append(f"✅ حجم: {p1['size']}ml")
            else:
                parts.append(f"🔄 حجم: {p1['size']}ml ↔ {p2['size']}ml")

        if p1["concentration"] and p2["concentration"]:
            if p1["concentration"] == p2["concentration"]:
                parts.append(f"✅ تركيز: {p1['concentration']}")
            else:
                parts.append(f"🔄 تركيز: {p1['concentration']} ↔ {p2['concentration']}")

        return " | ".join(parts) if parts else f"تشابه: {score:.0f}%"

    # ═══════════════════════════════════════════════════
    # 4. التحليل الشامل
    # ═══════════════════════════════════════════════════
    def analyze(self, my_products, competitor_products, competitor_name,
                session_id=None, progress_callback=None):
        """
        التحليل الشامل مع منع التكرار وتتبع المفقودات

        my_products: [{name, price, product_no, brand}, ...]
        competitor_products: [{name, price}, ...]

        يرجع: {
            higher: [...],    # سعرك أعلى
            lower: [...],     # سعرك أقل
            equal: [...],     # نفس السعر
            missing: [...],   # مفقود عندك
            review: [...],    # يحتاج مراجعة
            stats: {...},     # إحصائيات
            price_changes: [...],  # تغييرات الأسعار
        }
        """
        results = {
            "higher": [], "lower": [], "equal": [],
            "missing": [], "review": [], "price_changes": [],
            "stats": {"total_my": len(my_products), "total_comp": len(competitor_products)}
        }

        # ─── بناء فهرس منتجاتي ───
        my_index = {}
        for prod in my_products:
            name = str(prod.get("name", ""))
            fp = self.fingerprint(name, prod.get("brand"))
            my_index[fp] = prod
            # حفظ في قاعدة البيانات
            if self.db:
                parsed = self.parse_product(name)
                master_id = self.db.upsert_master_product(fp, {
                    "product_name": parsed["name"],
                    "brand": parsed["brand"],
                    "concentration": parsed["concentration"],
                    "size_ml": parsed["size"],
                })
                self.db.upsert_my_product(fp, {
                    "product_no": prod.get("product_no"),
                    "raw_name": name,
                    "price": prod.get("price"),
                    "brand": parsed["brand"],
                })
                self.db.add_alias(master_id, name.strip().lower(), "my_product")

        # ─── مطابقة كل منتج منافس ───
        matched_my_fps = set()
        total = len(competitor_products)

        for i, comp_prod in enumerate(competitor_products):
            if progress_callback:
                progress_callback((i + 1) / total, f"تحليل {i+1}/{total}")

            comp_name = str(comp_prod.get("name", ""))
            comp_price = comp_prod.get("price", 0)
            comp_fp = self.fingerprint(comp_name, comp_prod.get("brand"))

            if not comp_name.strip():
                continue

            # ─── البحث عن أفضل تطابق ───
            best_match = None
            best_score = 0
            best_fp = None

            # أولاً: بصمة مباشرة
            if comp_fp in my_index:
                best_match = my_index[comp_fp]
                best_score = 100
                best_fp = comp_fp
            else:
                # ثانياً: مطابقة ذكية
                for my_fp, my_prod in my_index.items():
                    if my_fp in matched_my_fps:
                        continue
                    result = self.match(str(my_prod.get("name", "")), comp_name)
                    if result["confidence"] > best_score:
                        best_score = result["confidence"]
                        best_match = my_prod
                        best_fp = my_fp
                        if best_score >= 97:
                            break

            # ─── تسجيل سعر المنافس (تراكمي) ───
            price_changed = False
            prev_price = None
            if self.db:
                price_changed, prev_price = self.db.record_competitor_price(
                    fingerprint=comp_fp,
                    competitor_name=competitor_name,
                    raw_name=comp_name,
                    price=comp_price,
                    session_id=session_id
                )

            # ─── تصنيف النتيجة ───
            if best_match and best_score >= MATCH_THRESHOLDS["medium"]:
                matched_my_fps.add(best_fp)
                my_price = best_match.get("price", 0) or 0
                diff = round(my_price - comp_price, 2)
                diff_pct = round((diff / comp_price * 100), 1) if comp_price else 0

                # تعلم تراكمي: حفظ الاسم كـ alias
                if self.db and best_score >= MATCH_THRESHOLDS["high"]:
                    alias_master = self.db.conn.execute(
                        "SELECT id FROM master_products WHERE fingerprint=?", (best_fp,)
                    ).fetchone()
                    if alias_master:
                        self.db.add_alias(alias_master["id"], comp_name.strip().lower(), "competitor")

                entry = {
                    "my_name": best_match.get("name", ""),
                    "my_price": my_price,
                    "comp_name": comp_name,
                    "comp_price": comp_price,
                    "diff": diff,
                    "diff_pct": diff_pct,
                    "confidence": best_score,
                    "product_no": best_match.get("product_no", ""),
                    "brand": best_match.get("brand", ""),
                    "competitor": competitor_name,
                    "fingerprint": best_fp,
                    "price_changed": price_changed,
                    "prev_price": prev_price,
                }

                if best_score < MATCH_THRESHOLDS["high"]:
                    entry["match_type"] = "review"
                    results["review"].append(entry)
                elif diff > 1:
                    entry["match_type"] = "higher"
                    results["higher"].append(entry)
                elif diff < -1:
                    entry["match_type"] = "lower"
                    results["lower"].append(entry)
                else:
                    entry["match_type"] = "equal"
                    results["equal"].append(entry)

                # تسجيل تغير السعر
                if price_changed:
                    results["price_changes"].append({
                        "comp_name": comp_name,
                        "competitor": competitor_name,
                        "old_price": prev_price,
                        "new_price": comp_price,
                        "change": round(comp_price - (prev_price or 0), 2),
                    })
            else:
                # ─── منتج مفقود — مع تحقق ذكي ───
                parsed = self.parse_product(comp_name)

                # البحث عن أقرب منتج عندي (حتى لو لم يصل للعتبة)
                possible_fp = None
                possible_name = None
                possible_score = best_score  # أفضل تشابه وجدناه

                if best_match and best_score >= 40:
                    possible_fp = best_fp
                    possible_name = best_match.get("name", "")

                if self.db:
                    self.db.record_missing_product(
                        fingerprint=comp_fp,
                        raw_name=comp_name,
                        competitor_name=competitor_name,
                        competitor_price=comp_price,
                        brand=parsed["brand"],
                        possible_match_fp=possible_fp,
                        possible_match_name=possible_name,
                        possible_match_score=possible_score,
                    )
                results["missing"].append({
                    "comp_name": comp_name,
                    "comp_price": comp_price,
                    "competitor": competitor_name,
                    "brand": parsed["brand"],
                    "best_score": best_score,
                    "fingerprint": comp_fp,
                    "possible_match_name": possible_name or "",
                    "possible_match_fp": possible_fp or "",
                    "possible_match_score": possible_score,
                })

        # ─── ترتيب النتائج ───
        results["higher"].sort(key=lambda x: x.get("diff_pct", 0), reverse=True)
        results["lower"].sort(key=lambda x: x.get("diff_pct", 0))
        results["missing"].sort(key=lambda x: x.get("comp_price", 0) or 0, reverse=True)

        # ─── الإحصائيات ───
        results["stats"].update({
            "matched": len(results["higher"]) + len(results["lower"]) + len(results["equal"]),
            "higher": len(results["higher"]),
            "lower": len(results["lower"]),
            "equal": len(results["equal"]),
            "missing": len(results["missing"]),
            "review": len(results["review"]),
            "price_changes": len(results["price_changes"]),
        })

        return results


# ═══════════════════════════════════════════════════
# SmartEngineV21 — مع AI كطبقة رابعة
# ═══════════════════════════════════════════════════
class SmartEngineV21(SmartEngine):
    """محرك v21 مع Gemini AI كطبقة رابعة للمطابقة الغامضة"""

    def __init__(self, db=None, ai_engine=None):
        super().__init__(db=db)
        self.ai = ai_engine

    def match(self, my_product: str, competitor_product: str):
        """مطابقة بـ 5 طبقات: بصمة → alias → حقول → AI → fallback"""
        base = super().match(my_product, competitor_product)
        conf = base["confidence"]

        # إذا كانت نتيجة الطبقات 3 واضحة، نُرجعها مباشرة
        if conf >= 85 or conf < 50:
            return base

        # ─── الطبقة 4: Gemini AI للحالات الغامضة (50-84%) ───
        if self.ai and self.ai.available:
            ai_result = self.ai.match_products(my_product, competitor_product)
            if ai_result.get("is_same") is not None:
                ai_conf = ai_result.get("confidence", conf)
                # دمج: نعطي وزن 60% للـ AI و 40% للمحرك الذكي
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
                    "details": f"🤖 AI: {ai_result.get('reason','')} | {base['details']}",
                    "ai_used": True,
                    "ai_source": ai_result.get("source", "gemini"),
                }

        return base

    def analyze(self, my_products, competitor_products, competitor_name,
                session_id=None, progress_callback=None):
        """تحليل شامل مع تقدم مفصّل"""
        results = super().analyze(
            my_products, competitor_products, competitor_name,
            session_id=session_id,
            progress_callback=progress_callback
        )
        # إضافة إحصائيات AI
        if self.ai:
            results["ai_stats"] = self.ai.stats
        return results
