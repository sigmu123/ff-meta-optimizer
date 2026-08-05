import json
import os

class TacticalParser:
    def __init__(self, patch_version="patch_v1"):
        self.base_path = f"data/patches/{patch_version}"
        
    def load_json(self, filename):
        file_filepath = os.path.join(self.base_path, filename)
        if os.path.exists(file_filepath):
            with open(file_filepath, 'r') as f:
                return json.load(f)
        return {}

    def query_system(self, user_prompt):
        prompt = user_prompt.lower()
        
        # Weapons & Items Search
        if any(w in prompt for w in ["gun", "weapon", "damage", "range", "vest", "item", "attachment"]):
            data = self.load_json("weapons/base_attributes.json")
            return {"category": "weapons_and_items", "data": data}
            
        # Character Skills Search
        elif any(c in prompt for c in ["character", "skill", "chrono", "wukong", "andrew", "shirou", "jai", "cooldown"]):
            data = self.load_json("characters.json")
            return {"category": "characters", "data": data}
            
        # Map & Mode Adjustments Search
        elif any(m in prompt for m in ["map", "clock tower", "mars electric", "clash squad", "vending", "revival", "zone"]):
            data = self.load_json("modes_and_maps.json")
            return {"category": "modes_and_maps", "data": data}
            
        # System Features & Settings Search
        elif any(s in prompt for s in ["replay", "guild", "setting", "split", "star", "bug"]):
            data = self.load_json("system_and_settings.json")
            return {"category": "system_and_settings", "data": data}
            
        return {"category": "general", "message": "No specific query patch match found."}

if __name__ == "__main__":
    parser = TacticalParser()
    test_query = "Clock tower me kya change hua tha?"
    result = parser.query_system(test_query)
    print(f"[PARSER TEST]: Query Keyword Matched Category -> {result['category']}")
