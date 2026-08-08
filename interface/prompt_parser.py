import os
import json
import google.generativeai as genai

class PromptParser:
    def __init__(self):
        # Fetch API key from Environment Variables (GitHub Secrets)
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def parse_roman_urdu_prompt(self, user_prompt):
        if not self.model:
            print("[-] API Key not found. Falling back to default 'rush' playstyle.")
            return "rush"

        sys_prompt = f"""
        You are a Free Fire Meta Optimizer AI. 
        Read the user's Roman Urdu prompt and output exactly ONE word describing their desired playstyle.
        Valid outputs ONLY: "rush", "sniper", "support", "camper".
        User Prompt: "{user_prompt}"
        """
        try:
            response = self.model.generate_content(sys_prompt)
            playstyle = response.text.strip().lower()
            if playstyle not in ["rush", "sniper", "support", "camper"]:
                return "rush"
            return playstyle
        except Exception as e:
            print(f"[-] API Parsing failed: {e}. Defaulting to rush.")
            return "rush"

if __name__ == "__main__":
    parser = PromptParser()
    raw_query = os.getenv("USER_QUERY", "mujhe rush game khelna ha")
    extracted_playstyle = parser.parse_roman_urdu_prompt(raw_query)
    
    # Export for the next GitHub Actions step
    with open(os.environ['GITHUB_ENV'], 'a') as f:
        f.write(f"FF_PLAYSTYLE={extracted_playstyle}\n")
    
    print(f"[*] Parsed Playstyle: {extracted_playstyle.upper()}")
