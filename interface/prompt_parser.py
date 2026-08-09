import os
import json
import sys
import google.generativeai as genai

class PromptParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use a valid model name (gemini-2.0-flash is current, fallback to 1.5-pro if needed)
            try:
                self.model = genai.GenerativeModel("gemini-2.0-flash")
            except Exception:
                self.model = genai.GenerativeModel("gemini-1.5-pro")
        else:
            self.model = None

    def parse_intent(self, user_query: str) -> dict:
        """
        Parse user query into structured parameters.
        """
        query_lower = user_query.lower()
        parsed = {
            "mode": "br",
            "objective": "max_damage",
            "playstyle": "rush",
            "engagement_range": "mid",
            "patch": "patch_ob54"
        }

        # --- Rule-based detection (always runs) ---
        if "cs" in query_lower or "clash squad" in query_lower:
            parsed["mode"] = "cs"
        if "sniper" in query_lower:
            parsed["playstyle"] = "sniper"
        if "ttk" in query_lower or "time to kill" in query_lower:
            parsed["objective"] = "min_ttk"
        if "damage" in query_lower and "block" not in query_lower:
            parsed["objective"] = "max_damage"

        # --- NEW: detect survival/tank/block keywords ---
        survival_keywords = ["block", "tank", "defend", "protect", "survive", "survival", "damage ko block"]
        if any(kw in query_lower for kw in survival_keywords):
            parsed["objective"] = "survival"
            parsed["playstyle"] = "tank"

        # Override with Gemini if available
        if self.model and len(user_query.strip()) > 5:
            try:
                prompt = f"""
You are a Free Fire meta analyst. Parse the following user query and return a JSON object with exactly these keys:
- "mode": "br" or "cs"
- "objective": "max_damage", "min_ttk", or "survival"
- "playstyle": "rush", "sniper", "passive", "tank", or "balanced"
- "engagement_range": "close", "mid", or "long"
- "patch": a patch folder name like "patch_ob54" (infer if mentioned, else "patch_ob54")

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
                        for key in data:
                            if key in parsed:
                                parsed[key] = data[key]
            except Exception as e:
                print(f"Gemini parsing failed: {e}", file=sys.stderr)
        return parsed

def parse_user_prompt(user_query: str) -> str:
    parser = PromptParser()
    parsed = parser.parse_intent(user_query)
    return parsed.get("playstyle", "rush")

def parse_full_prompt(user_query: str) -> dict:
    parser = PromptParser()
    return parser.parse_intent(user_query)
