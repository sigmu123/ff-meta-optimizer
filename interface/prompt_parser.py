import os
import json
import sys
import google.generativeai as genai

class PromptParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            try:
                self.model = genai.GenerativeModel("gemini-3.6-flash")
            except Exception:
                try:
                    self.model = genai.GenerativeModel("gemini-2.0-flash")
                except Exception:
                    self.model = genai.GenerativeModel("gemini-1.5-pro")
        else:
            self.model = None

    def parse_intent(self, user_query: str) -> dict:
        query_lower = user_query.lower()
        parsed = {
            "mode": "br",
            "objective": "max_damage",
            "playstyle": "rush",
            "engagement_range": "mid",
            "patch": "patch_ob54",
            "response_type": "full_build"   # NEW
        }

        # Step 1: Gemini (if available)
        if self.model and len(user_query.strip()) > 3:
            try:
                prompt = f"""
You are a Free Fire meta analyst. Parse the user's query and return JSON with:
- "mode": "br" or "cs"
- "objective": one of ["max_damage", "min_ttk", "survival", "max_healing", "balanced", "max_squad_damage", "max_squad_survival", "custom"]
- "playstyle": one of ["rush", "sniper", "tank", "healer", "support", "aggressive", "defensive", "balanced", "stealth", "versatile"]
- "engagement_range": one of ["close", "mid", "long"]
- "patch": folder name (e.g., "patch_ob54")
- "response_type": one of ["full_build", "weapon_only", "character_only", "loadout_only", "explanation"]

Rules:
- If user asks about "gun", "weapon", "sniper", "rifle", "damage gun" → response_type = "weapon_only"
- If user asks about "character", "skill" → response_type = "character_only"
- If user mentions "long range" → playstyle = "sniper", engagement_range = "long"
- If user mentions "damage" → objective = "max_damage"
- If none, choose appropriate.

Return ONLY JSON.
Query: {user_query}
"""
                response = self.model.generate_content(prompt)
                if response and response.text:
                    text = response.text.strip()
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start != -1 and end > start:
                        data = json.loads(text[start:end])
                        for key in data:
                            if key in parsed:
                                parsed[key] = data[key]
                        # Validate
                        if parsed["objective"] not in ["max_damage", "min_ttk", "survival", "max_healing", "balanced", "max_squad_damage", "max_squad_survival", "custom"]:
                            parsed["objective"] = "max_damage"
                        if parsed["playstyle"] not in ["rush", "sniper", "tank", "healer", "support", "aggressive", "defensive", "balanced", "stealth", "versatile"]:
                            parsed["playstyle"] = "rush"
                        if parsed["response_type"] not in ["full_build", "weapon_only", "character_only", "loadout_only", "explanation"]:
                            parsed["response_type"] = "full_build"
                        return parsed
            except Exception as e:
                print(f"Gemini error: {e}", file=sys.stderr)

        # Step 2: Fallback rules
        if "cs" in query_lower or "clash squad" in query_lower:
            parsed["mode"] = "cs"

        if any(kw in query_lower for kw in ["heal", "healing", "medkit"]):
            parsed["objective"] = "max_healing"
        elif "ttk" in query_lower:
            parsed["objective"] = "min_ttk"
        elif any(kw in query_lower for kw in ["survive", "tank"]):
            parsed["objective"] = "survival"
        elif "damage" in query_lower:
            parsed["objective"] = "max_damage"

        if "sniper" in query_lower or "long range" in query_lower:
            parsed["playstyle"] = "sniper"
            parsed["engagement_range"] = "long"
        elif "heal" in query_lower:
            parsed["playstyle"] = "healer"
        elif "tank" in query_lower:
            parsed["playstyle"] = "tank"
        elif "rush" in query_lower:
            parsed["playstyle"] = "rush"

        if any(kw in query_lower for kw in ["gun", "weapon", "rifle", "sniper", "shotgun", "smg"]):
            parsed["response_type"] = "weapon_only"
        elif any(kw in query_lower for kw in ["character", "skill", "hero"]):
            parsed["response_type"] = "character_only"
        elif any(kw in query_lower for kw in ["loadout", "pet"]):
            parsed["response_type"] = "loadout_only"
        elif any(kw in query_lower for kw in ["build", "combination", "setup"]):
            parsed["response_type"] = "full_build"

        import re
        patch_match = re.search(r'(ob\d{2}|v\d{4}_\d{2}_\d{2}|patch_\w+)', query_lower)
        if patch_match:
            parsed["patch"] = patch_match.group(0)

        return parsed

def parse_user_prompt(user_query: str) -> str:
    parser = PromptParser()
    parsed = parser.parse_intent(user_query)
    return parsed.get("playstyle", "rush")

def parse_full_prompt(user_query: str) -> dict:
    parser = PromptParser()
    return parser.parse_intent(user_query)
