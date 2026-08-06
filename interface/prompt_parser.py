import json
import os

class TacticalParser:
    def __init__(self, patch_version="patch_v33_heroes_arise"):
        self.base_path = os.path.join("data", "patches", patch_version)
        
    def load_json(self, relative_path):
        filepath = os.path.join(self.base_path, relative_path)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def query_system(self, user_prompt):
        prompt = user_prompt.lower()
        
        # Safe Multi-Format Reader
        base_attrs = self.load_json(os.path.join("weapons", "base_attributes.json"))
        if not base_attrs:
            base_attrs = self.load_json("weapons.json")
            
        range_decay = self.load_json(os.path.join("weapons", "range_decay.json"))

        active = self.load_json(os.path.join("characters", "active_skills.json"))
        passive = self.load_json(os.path.join("characters", "passive_skills.json"))
        synergies = self.load_json(os.path.join("characters", "synergies.json"))
        
        direct_chars = self.load_json("characters.json")
        if not direct_chars:
            direct_chars = self.load_json(os.path.join("characters", "characters.json"))

        utilities = self.load_json(os.path.join("mechanics", "utilities.json"))
        if not utilities:
            utilities = self.load_json("modes_and_maps.json")

        # Category Intent Classification
        if any(w in prompt for w in ["gun", "weapon", "m24", "g36", "mp5", "mp40", "m1887", "ump", "kar98k"]) and not any(c in prompt for c in ["kenta", "a124", "steffie"]):
            cat = "weapons_and_items"
        elif any(c in prompt for c in ["character", "skill", "kenta", "a124", "steffie", "nikita", "caroline", "otho", "rafael", "thiva", "chrono", "wukong", "alok"]):
            cat = "characters"
        elif any(m in prompt for m in ["map", "clash squad", "vending", "revival", "zone"]):
            cat = "modes_and_maps"
        else:
            cat = "weapons_and_items"

        return {
            "category": cat,
            "data": {
                "base_attributes": base_attrs if isinstance(base_attrs, dict) else {"weapons": base_attrs},
                "range_decay": range_decay,
                "active_skills": active if active else direct_chars,
                "passive_skills": passive if passive else direct_chars,
                "synergies": synergies,
                "characters": direct_chars,
                "modes_and_maps": utilities,
                "clash_squad_economy": utilities.get("clash_squad_economy", {}) if isinstance(utilities, dict) else {},
                "loot_and_vending": utilities.get("loot_and_vending", {}) if isinstance(utilities, dict) else {}
            }
        }
