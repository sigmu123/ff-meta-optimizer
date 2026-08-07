import re
from typing import Dict, Any

class PromptParser:
    """
    Parses natural language query input into structured parameters for the execution engine.
    """
    @staticmethod
    def parse(prompt_string: str) -> Dict[str, Any]:
        prompt_lower = prompt_string.lower()
        
        mode = "clash_squad"
        if "br" in prompt_lower or "battle royale" in prompt_lower:
            mode = "battle_royale"
        elif "cs" in prompt_lower or "clash squad" in prompt_lower:
            mode = "clash_squad"

        playstyle = "balanced"
        if "rush" in prompt_lower or "aggro" in prompt_lower or "close" in prompt_lower:
            playstyle = "rush"
        elif "sniper" in prompt_lower or "long" in prompt_lower or "defense" in prompt_lower:
            playstyle = "sniper"
        elif "support" in prompt_lower or "heal" in prompt_lower:
            playstyle = "support"

        return {
            "mode": mode,
            "playstyle": playstyle,
            "raw_prompt": prompt_string
        }
