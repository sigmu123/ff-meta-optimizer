import sys
from core.ttk_calculator import MechanicsEngine
from interface.prompt_parser import TacticalParser

class AdvisorEngine:
    def __init__(self, patch_version="patch_v1"):
        self.parser = TacticalParser(patch_version)
        
    def process_query(self, query):
        parsed = self.parser.query_system(query)
        cat = parsed["category"]
        data = parsed.get("data", {})
        
        print(f"\n[QUERY RECEIVED]: '{query}'")
        print(f"[TACTICAL CATEGORY]: {cat.upper()}")
        print("-" * 50)
        
        if cat == "weapons_and_items":
            print("ITEMS & WEAPON ADJUSTMENTS DETECTED:")
            for item in data.get("new_items", []):
                print(f" -> New Item: {item['name']} ({item['category']})")
            for w in data.get("weapon_adjustments", []):
                print(f" -> Modified: {w['name']} | Adjustments: {w['stat_changes']}")
                
        elif cat == "characters":
            print("CHARACTER SKILL ADJUSTMENTS DETECTED:")
            for c in data.get("character_adjustments", []):
                print(f" -> Character: {c['name']} | Skill: {c['skill_name']} | Changes: {c.get('changes', c.get('item_addition'))}")
                
        elif cat == "modes_and_maps":
            print("MAP & MODE MODIFICATIONS DETECTED:")
            cs = data.get("clash_squad", {})
            print(f" -> CS Mode: {cs.get('custom_room_mode')}")
            for map_adj in cs.get("map_adjustments", []):
                print(f" -> Map Change [{map_adj['location']}]: {map_adj['change']}")
                
        elif cat == "system_and_settings":
            print("SYSTEM & QUALITY OF LIFE UPDATES DETECTED:")
            for sys_feat in data.get("new_systems", []):
                print(f" -> Feature: {sys_feat['feature']} ({sys_feat['availability']})")
        else:
            print("[INFO]: No direct patch adjustments found for this specific query.")

if __name__ == "__main__":
    engine = AdvisorEngine("patch_v1")
    
    # Test sample prompts
    engine.process_query("Clock tower me kya map change hua?")
    engine.process_query("Chrono aur Wukong me kya nerf aaya?")
