import json
import os

class TacticalParser:
    def __init__(self, patch_version="patch_v33_heroes_arise"):
        self.base_path = os.path.join("data", "patches", patch_version)
        
    def load_json(self, relative_path):
        filepath = os.path.join(self.base_path, relative_path)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def query_system(self, user_prompt):
        prompt = user_prompt.lower()
        
        # Weapons & Items Search
        if any(w in prompt for w in ["gun", "weapon", "damage", "range", "vest", "item", "attachment", "g36", "mp5", "mp40", "m1887", "ump", "kar98k"]):
            base_attrs = self.load_json(os.path.join("weapons", "base_attributes.json"))
            range_decay = self.load_json(os.path.join("weapons", "range_decay.json"))
            return {
                "category": "weapons_and_items", 
                "data": {
                    "base_attributes": base_attrs,
                    "range_decay": range_decay
                }
            }
            
        # Character Skills Search
        elif any(c in prompt for c in ["character", "skill", "kenta", "a124", "steffie", "nikita", "caroline", "otho", "rafael", "thiva", "chrono", "wukong", "cooldown", "synergy"]):
            active = self.load_json(os.path.join("characters", "active_skills.json"))
            passive = self.load_json(os.path.join("characters", "passive_skills.json"))
            synergies = self.load_json(os.path.join("characters", "synergies.json"))
            return {
                "category": "characters", 
                "data": {
                    "active_skills": active,
                    "passive_skills": passive,
                    "synergies": synergies
                }
            }
            
        # Map & Mode Adjustments Search
        elif any(m in prompt for m in ["map", "clock tower", "mars electric", "clash squad", "vending", "revival", "zone", "mission", "hit list", "supply run"]):
            data = self.load_json(os.path.join("mechanics", "utilities.json"))
            return {"category": "modes_and_maps", "data": data}
            
        # System Features & Settings Search
        elif any(s in prompt for s in ["replay", "guild", "setting", "split", "star", "bug"]):
            data = self.load_json(os.path.join("mechanics", "utilities.json"))
            return {"category": "system_and_settings", "data": data}
            
        return {"category": "general", "message": "No specific query patch match found."}

if __name__ == "__main__":
    parser = TacticalParser("patch_v33_heroes_arise")
    test_query = "Kenta aur G36 me kya stats hain?"
    result = parser.query_system(test_query)
    print(f"[PARSER TEST]: Query Keyword Matched Category -> {result['category']}")
