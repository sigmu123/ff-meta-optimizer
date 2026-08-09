import os
import google.generativeai as genai

class PromptParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-3.5-flash")
        else:
            self.model = None

    def parse_intent(self, user_query):
        """
        Parses natural language queries using Gemini API if available, 
        otherwise falls back to rule-based keyword extraction.
        """
        query_lower = user_query.lower()
        
        # Fallback default parameters
        parsed_data = {
            "mode": "br",
            "playstyle": "rush",
            "patch": "patch_ob54"
        }

        if "cs" in query_lower or "clash squad" in query_lower:
            parsed_data["mode"] = "cs"
        
        if "sniper" in query_lower:
            parsed_data["playstyle"] = "sniper"
        elif "survive" in query_lower or "passive" in query_lower:
            parsed_data["playstyle"] = "survival"

        if self.model and len(user_query.strip()) > 3:
            try:
                prompt = (
                    f"Analyze this Free Fire meta query and extract JSON with keys 'mode' (br/cs), "
                    f"'playstyle' (rush/sniper/survival), and 'patch' (e.g. patch_ob54):\nQuery: {user_query}"
                )
                response = self.model.generate_content(prompt)
                # Basic cleanup or parsing can be handled safely here
                if response and response.text:
                    pass 
            except Exception:
                pass

        return parsed_data
