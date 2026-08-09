import os
from google import genai

def parse_user_prompt(prompt_text):
    """
    Parses user prompt using the latest Google GenAI SDK.
    Returns one of the valid playstyles: 'rush', 'survival', or 'sniper'.
    """
    if not prompt_text or not isinstance(prompt_text, str):
        return "rush"

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY environment variable missing. Defaulting to rush.")
        return "rush"

    try:
        # Initialize modern Google GenAI Client
        client = genai.Client(api_key=api_key)
        
        # Call latest Gemini 2.5 Flash model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=(
                "Analyze this Free Fire playstyle query and return ONLY one word "
                "('rush', 'survival', or 'sniper'): " + str(prompt_text)
            ),
        )
        
        if response and hasattr(response, 'text') and response.text:
            playstyle = response.text.strip().lower()
            if playstyle in ["rush", "survival", "sniper"]:
                return playstyle

        return "rush"

    except Exception as e:
        print(f"[-] API Parsing failed: {e}. Defaulting to rush.")
        return "rush"


if __name__ == "__main__":
    # Quick standalone testing handler
    test_prompt = os.getenv("TEST_PROMPT", "I want an aggressive rusher loadout")
    result = parse_user_prompt(test_prompt)
    print(f"[+] Parsed Playstyle: {result}")
