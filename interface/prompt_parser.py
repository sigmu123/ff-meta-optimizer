import os
import json
import google.generativeai as genai

class PromptParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    def parse_intent(self, user_query: str) -> dict:
        """
        Gemini یا rule-based طریقے سے پرامپٹ کو مندرجہ ذیل کلیدوں والی dict میں بدلتا ہے:
            - mode: "br" یا "cs"
            - objective: "max_damage", "min_ttk", "survival"
            - playstyle: "rush", "sniper", "passive"
            - engagement_range: "close", "mid", "long" (اختیاری)
            - patch: جیسے "patch_ob54"
        """
        query_lower = user_query.lower()
        # ڈیفالٹ
        parsed = {
            "mode": "br",
            "objective": "max_damage",
            "playstyle": "rush",
            "engagement_range": "mid",
            "patch": "patch_ob54"
        }

        # بنیادی rule-based detection (Gemini ناکام ہونے کی صورت میں)
        if "cs" in query_lower or "clash squad" in query_lower:
            parsed["mode"] = "cs"
        if "sniper" in query_lower:
            parsed["playstyle"] = "sniper"
        if "survive" in query_lower or "passive" in query_lower:
            parsed["playstyle"] = "survival"
        if "ttk" in query_lower or "time to kill" in query_lower:
            parsed["objective"] = "min_ttk"
        if "damage" in query_lower:
            parsed["objective"] = "max_damage"

        # اگر Gemini دستیاب ہو تو مزید تفصیلی تجزیہ
        if self.model and len(user_query.strip()) > 5:
            try:
                prompt = f"""
You are a Free Fire meta analyst. Parse the following user query and return a JSON object with exactly these keys:
- "mode": "br" or "cs"
- "objective": "max_damage", "min_ttk", or "survival"
- "playstyle": "rush", "sniper", "passive", or "balanced"
- "engagement_range": "close", "mid", or "long"
- "patch": a patch folder name like "patch_ob54" (infer from query if mentioned, else "patch_ob54")

Query: {user_query}

Return ONLY the JSON object, no extra text.
"""
                response = self.model.generate_content(prompt)
                if response and response.text:
                    text = response.text
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = text[start:end]
                        data = json.loads(json_str)
                        # صرف موجودہ کلیدوں کو اوور رائڈ کریں
                        for key in data:
                            if key in parsed:
                                parsed[key] = data[key]
            except Exception as e:
                print(f"Gemini parsing failed: {e}")
        return parsed


# ---- workflow کے لیے ٹاپ‑لیول فنکشن ----
def parse_user_prompt(user_query: str) -> str:
    """
    GitHub Actions workflow سے براہ راست کال ہوتی ہے۔
    صرف playstyle لوٹاتی ہے تاکہ پچھلی مطابقت برقرار رہے۔
    """
    parser = PromptParser()
    parsed = parser.parse_intent(user_query)
    return parsed.get("playstyle", "rush")


# نیا فنکشن: مکمل پیرامیٹرز حاصل کرنے کے لیے
def parse_full_prompt(user_query: str) -> dict:
    parser = PromptParser()
    return parser.parse_intent(user_query)
