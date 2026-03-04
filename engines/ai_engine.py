"""
مهووس v22 — محرك الذكاء الاصطناعي (Gemini)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• يُستدعى فقط عند الحالات الغامضة (50–84%)
• يعالج المطابقة العربية↔الإنجليزية
• دعم مفاتيح متعددة مع تدوير تلقائي
• Cache داخلي لتقليل الاستهلاك
• دعم Fragrantica للمنتجات المفقودة
"""

import json, re, time, hashlib
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIEngine:
    """محرك Gemini AI للمطابقة الذكية"""

    def __init__(self, api_keys: list = None):
        self.api_keys = api_keys or []
        self.current_key_idx = 0
        self._cache = {}
        self._calls_count = 0
        self._errors_count = 0
        self.available = GEMINI_AVAILABLE and bool(self.api_keys)

        if self.available:
            self._init_model()

    # ─────────────────────────────────────────────
    # تهيئة النموذج
    # ─────────────────────────────────────────────
    def _init_model(self):
        if not self.api_keys or not GEMINI_AVAILABLE:
            self.available = False
            return

        try:
            key = self.api_keys[self.current_key_idx % len(self.api_keys)]
            genai.configure(api_key=key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={"temperature": 0.1, "max_output_tokens": 256}
            )
            self.available = True
        except Exception:
            self.available = False

    def _rotate_key(self):
        """تدوير مفتاح API عند الخطأ"""
        if len(self.api_keys) > 1:
            self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
            self._init_model()

    # ─────────────────────────────────────────────
    # Cache
    # ─────────────────────────────────────────────
    def _cache_key(self, name1: str, name2: str = "") -> str:
        return hashlib.md5(f"{name1.lower().strip()}||{name2.lower().strip()}".encode()).hexdigest()

    # ─────────────────────────────────────────────
    # مطابقة المنتجات
    # ─────────────────────────────────────────────
    def match_products(self, product1: str, product2: str, context: dict = None) -> dict:
        """
        يُستدعى فقط عند confidence بين 50–84%
        """
        if not self.available:
            return {"confidence": None, "is_same": None, "reason": "AI غير متاح", "source": "no_ai"}

        ck = self._cache_key(product1, product2)
        if ck in self._cache:
            cached = self._cache[ck].copy()
            cached["source"] = "cache"
            return cached

        prompt = self._build_prompt(product1, product2, context)
        result = self._call_gemini(prompt)

        if result:
            self._cache[ck] = result

        return result or {"confidence": None, "is_same": None, "reason": "فشل AI", "source": "error"}

    def _build_prompt(self, p1: str, p2: str, context: dict = None) -> str:
        ctx = f"\nسياق إضافي: {json.dumps(context, ensure_ascii=False)}" if context else ""
        return f"""
أنت خبير في مطابقة منتجات العطور. قرر إذا كان هذان المنتجان نفس الشيء.

منتج 1: "{p1}"
منتج 2: "{p2}"{ctx}

قواعد مهمة:
- "ديور سوفاج" = "Dior Sauvage" (نفس المنتج) ✅
- "EDP" ≠ "EDT" (تركيز مختلف) ❌
- "100ml" ≠ "200ml" (حجم مختلف) ❌
- إذا لم يُذكر الحجم أو النوع، افترض أنهما محتملان نفس المنتج

أجب فقط بـ JSON:
{{"is_same": true/false, "confidence": 85, "reason": "سبب قصير"}}
"""

    def _call_gemini(self, prompt: str, retries: int = 2) -> Optional[dict]:
        for attempt in range(retries + 1):
            try:
                response = self.model.generate_content(prompt)
                text = response.text.strip()

                json_match = re.search(r'\{[^\}]+\}', text)
                if json_match:
                    data = json.loads(json_match.group())
                    self._calls_count += 1
                    return {
                        "confidence": float(data.get("confidence", 0)),
                        "is_same": bool(data.get("is_same", False)),
                        "reason": data.get("reason", ""),
                        "source": "gemini"
                    }

            except Exception as e:
                self._errors_count += 1
                err = str(e).lower()

                if "quota" in err or "rate" in err or "429" in err:
                    self._rotate_key()
                    time.sleep(1)

                elif attempt < retries:
                    time.sleep(0.5)

        return None

    # ─────────────────────────────────────────────
    # إثراء المنتجات المفقودة
    # ─────────────────────────────────────────────
    def enrich_missing_product(self, product_name: str) -> dict:
        if not self.available:
            return {}

        ck = self._cache_key("enrich_" + product_name)
        if ck in self._cache:
            return self._cache[ck]

        prompt = f"""
أنت خبير عطور. استخرج معلومات عن هذا المنتج:
"{product_name}"

أجب فقط بـ JSON:
{{"brand": "الماركة", "product_line": "اسم الخط", "concentration": "edp/edt/parfum",
"size_ml": 100, "gender": "men/women/unisex", "description": "وصف قصير بالعربي"}}
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            json_match = re.search(r'\{[^\}]+\}', text, re.DOTALL)

            if json_match:
                data = json.loads(json_match.group())
                self._cache[ck] = data
                self._calls_count += 1
                return data

        except Exception:
            pass

        return {}

    # ─────────────────────────────────────────────
    # اقتراح سعر ذكي
    # ─────────────────────────────────────────────
    def suggest_price(self, my_price: float, competitor_prices: dict) -> dict:
        if not competitor_prices:
            return {}

        # fallback بدون AI
        if not self.available:
            prices = list(competitor_prices.values())
            avg = sum(prices) / len(prices)
            return {
                "suggested_price": round(avg, 2),
                "strategy": "متوسط المنافسين",
                "source": "calculation"
            }

        prices_text = "\n".join([f"- {k}: {v} ريال" for k, v in competitor_prices.items()])

        prompt = f"""
أنت خبير تسعير عطور في السوق السعودي.

سعري الحالي: {my_price} ريال
أسعار المنافسين:
{prices_text}

اقترح سعراً مثالياً مع استراتيجية.
أجب بـ JSON:
{{"suggested_price": 450, "strategy": "أقل بـ 5%", "min_price": 420, "max_price": 480, "reasoning": "سبب"}}
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            json_match = re.search(r'\{[^\}]+\}', text, re.DOTALL)

            if json_match:
                data = json.loads(json_match.group())
                data["source"] = "gemini"
                self._calls_count += 1
                return data

        except Exception:
            pass

        # fallback
        prices = list(competitor_prices.values())
        avg = sum(prices) / len(prices)
        return {
            "suggested_price": round(avg * 0.97, 2),
            "strategy": "أقل بـ 3% من المتوسط",
            "source": "calculation"
        }

    # ─────────────────────────────────────────────
    # إحصائيات
    # ─────────────────────────────────────────────
    @property
    def stats(self) -> dict:
        return {
            "available": self.available,
            "calls": self._calls_count,
            "errors": self._errors_count,
            "cache_size": len(self._cache),
            "active_key": self.current_key_idx + 1 if self.api_keys else 0,
            "total_keys": len(self.api_keys),
        }
