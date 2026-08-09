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
        """
        Parse user query into structured parameters using Gemini (primary) and rules (fallback).
        """
        query_lower = user_query.lower()
        parsed = {
            "mode": "br",
            "objective": "max_damage",
            "playstyle": "rush",
            "engagement_range": "mid",
            "patch": "patch_ob54"
        }

        # ---- Step 1: Try Gemini first (if available) ----
        if self.model and len(user_query.strip()) > 3:
            try:
                prompt = f"""
You are a Free Fire meta analyst. Your task is to parse the user's query and return a JSON object with EXACTLY these keys:
- "mode": "br" or "cs" (infer from query, e.g., "Clash Squad" -> "cs", "battle royale" -> "br")
- "objective": one of ["max_damage", "min_ttk", "survival", "max_healing", "balanced", "max_squad_damage", "max_squad_survival", "custom"]
  - "max_damage" – user wants highest damage output
  - "min_ttk" – user wants lowest time‑to‑kill
  - "survival" – user wants to survive longer (tank, defense)
  - "max_healing" – user wants maximum healing (self or team)
  - "balanced" – user wants a mix of damage and survival
  - "max_squad_damage" – user wants to maximize total squad damage
  - "max_squad_survival" – user wants squad to be hard to kill
  - "custom" – if none of the above fits, but try to map to one
- "playstyle": one of ["rush", "sniper", "tank", "healer", "support", "aggressive", "defensive", "balanced", "stealth", "versatile"]
- "engagement_range": one of ["close", "mid", "long"]
- "patch": a folder name like "patch_ob54" (if user mentions a specific patch, else use "patch_ob54")

Rules:
- If user mentions "heal", "recover", "medkit", "support" → objective = "max_healing", playstyle = "healer"
- If user mentions "damage", "kill", "high dps" → objective = "max_damage", playstyle = "rush" (or "sniper" if sniping mentioned)
- If user mentions "survive", "tank", "defense", "shield" → objective = "survival", playstyle = "tank"
- If user mentions "squad", "team", "all teammates" → objective = "max_squad_damage" or "max_squad_survival"
- If user mentions "ttk", "time to kill" → objective = "min_ttk"
- If none of these, choose the most appropriate based on overall context.

Return ONLY the JSON object, no extra text.

Query: {user_query}
"""
                response = self.model.generate_content(prompt)
                if response and response.text:
                    text = response.text.strip()
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = text[start:end]
                        data = json.loads(json_str)
                        for key in data:
                            if key in parsed:
                                parsed[key] = data[key]
                        # Validate values
                        if parsed["objective"] not in ["max_damage", "min_ttk", "survival", "max_healing", "balanced", "max_squad_damage", "max_squad_survival", "custom"]:
                            parsed["objective"] = "max_damage"
                        if parsed["playstyle"] not in ["rush", "sniper", "tank", "healer", "support", "aggressive", "defensive", "balanced", "stealth", "versatile"]:
                            parsed["playstyle"] = "rush"
                        return parsed
            except Exception as e:
                print(f"Gemini parsing failed: {e}", file=sys.stderr)

        # ---- Step 2: Fallback rule-based (enhanced) ----
        # Mode
        if "cs" in query_lower or "clash squad" in query_lower:
            parsed["mode"] = "cs"

        # Objective
        if any(kw in query_lower for kw in ["heal", "healing", "medkit", "recover", "support"]):
            parsed["objective"] = "max_healing"
        elif "ttk" in query_lower or "time to kill" in query_lower:
            parsed["objective"] = "min_ttk"
        elif any(kw in query_lower for kw in ["survive", "tank", "defend", "shield"]):
            parsed["objective"] = "survival"
        elif "squad" in query_lower or "team" in query_lower:
            if "damage" in query_lower:
                parsed["objective"] = "max_squad_damage"
            elif "survive" in query_lower or "defend" in query_lower:
                parsed["objective"] = "max_squad_survival"
            else:
                parsed["objective"] = "balanced"
        elif "damage" in query_lower:
            parsed["objective"] = "max_damage"
        else:
            parsed["objective"] = "max_damage"

        # Playstyle
        if "sniper" in query_lower:
            parsed["playstyle"] = "sniper"
        elif any(kw in query_lower for kw in ["heal", "support"]):
            parsed["playstyle"] = "healer"
        elif any(kw in query_lower for kw in ["tank", "defend"]):
            parsed["playstyle"] = "tank"
        elif "rush" in query_lower or "aggressive" in query_lower:
            parsed["playstyle"] = "rush"
        else:
            parsed["playstyle"] = "rush"

        # Engagement range
        if "close" in query_lower or "short" in query_lower:
            parsed["engagement_range"] = "close"
        elif "long" in query_lower or "far" in query_lower:
            parsed["engagement_range"] = "long"
        else:
            parsed["engagement_range"] = "mid"

        # Patch
        import re
        patch_match = re.search(r'(ob\d{2}|v\d{4}_\d{2}_\d{2}|patch_\w+)', query_lower)
        if patch_match:
            parsed["patch"] = patch_match.group(0)
        else:
            parsed["patch"] = "patch_ob54"

        return parsed

def parse_user_prompt(user_query: str) -> str:
    parser = PromptParser()
    parsed = parser.parse_intent(user_query)
    return parsed.get("playstyle", "rush")

def parse_full_prompt(user_query: str) -> dict:
    parser = PromptParser()
    return parser.parse_intent(user_query)
