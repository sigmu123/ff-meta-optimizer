import os
import google.generativeai as genai

class PromptParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")  # corrected model name
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
                if response and response.text:
                    # Attempt to parse JSON from response (simplified)
                    import json
                    # try to extract JSON block
                    text = response.text
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = text[start:end]
                        data = json.loads(json_str)
                        if 'playstyle' in data:
                            parsed_data['playstyle'] = data['playstyle']
            except Exception:
                pass

        return parsed_data


# ---- Added function for workflow integration ----
def parse_user_prompt(user_query: str) -> str:
    """
    Top-level function that returns the playstyle string.
    Called directly from the GitHub Actions workflow.
    """
    parser = PromptParser()
    parsed = parser.parse_intent(user_query)
    return parsed.get("playstyle", "rush")
