import re
from typing import Dict, Any

class PromptParser:
    @staticmethod
    def parse(prompt_text: str) -> Dict[str, Any]:
        """
        Parses raw Roman Urdu or English user prompts into structured parameters.
        Extracts patch version, game mode, playstyle, and primary stat intent.
        """
        text = prompt_text.lower().strip()

        # 1. Extract Patch Version (e.g., ob34, ob54, patch_ob52)
        patch_match = re.search(r'(ob\d+|patch_[a-z0-9_]+|v\d+)', text)
        patch_version = patch_match.group(1) if patch_match else "patch_ob54"
        if not patch_version.startswith("patch_") and patch_version.startswith("ob"):
            patch_version = f"patch_{patch_version}"

        # 2. Extract Game Mode (CS vs BR)
        if any(term in text for term in ["cs", "clash squad", "round"]):
            mode = "clash_squad"
        elif any(term in text for term in ["br", "battle royale", "map", "zone"]):
            mode = "battle_royale"
        else:
            mode = "clash_squad"

        # 3. Extract Playstyle Intent
        if any(term in text for term in ["rush", "fast", "speed", "close range"]):
            playstyle = "rush"
        elif any(term in text for term in ["defense", "hold", "camp", "shield", "cover"]):
            playstyle = "defense"
        elif any(term in text for term in ["sniper", "long range", "support"]):
            playstyle = "support"
        else:
            playstyle = "balanced"

        # 4. Extract Damage / Stat Preference
        if any(term in text for term in ["high damage", "heavy dmg", "dps", "kill"]):
            focus = "damage"
        elif any(term in text for term in ["heal", "hp", "survival"]):
            focus = "survival"
        else:
            focus = "balanced"

        return {
            "patch_version": patch_version,
            "mode": mode,
            "playstyle": playstyle,
            "focus": focus,
            "raw_prompt": prompt_text
        }


if __name__ == "__main__":
    test_prompt = "OB54 CS Ranked rush build with high damage"
    parsed = PromptParser.parse(test_prompt)
    print("[PARSER UNIT TEST]:", parsed)
