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
                print(f" -> New Item: {item.get('name', 'N/A')} ({item.get('category', 'N/A')})")
            for w in data.get("weapon_adjustments", []):
                print(f" -> Modified: {w.get('name', 'N/A')} | Adjustments: {w.get('stat_changes', {})}")
                
        elif cat == "characters":
            print("CHARACTER SKILL ADJUSTMENTS DETECTED:")
            for c in data.get("character_adjustments", []):
                char_name = c.get("name", "Unknown Character")
                skill_name = c.get("skill_name", "N/A")
                changes = c.get("changes", c.get("item_addition", "No change detail"))
                print(f" -> Character: {char_name} | Skill: {skill_name} | Changes: {changes}")
                
        elif cat == "modes_and_maps":
            print("MAP & MODE MODIFICATIONS DETECTED:")
            cs = data.get("clash_squad", {})
            print(f" -> CS Mode: {cs.get('custom_room_mode', 'N/A')}")
            for map_adj in cs.get("map_adjustments", []):
                print(f" -> Map Change [{map_adj.get('location', 'N/A')}]: {map_adj.get('change', 'N/A')}")
                
        elif cat == "system_and_settings":
            print("SYSTEM & QUALITY OF LIFE UPDATES DETECTED:")
            for sys_feat in data.get("new_systems", []):
                print(f" -> Feature: {sys_feat.get('feature', 'N/A')} ({sys_feat.get('availability', 'N/A')})")
        else:
            print("[INFO]: No direct patch adjustments found for this specific query.")

if __name__ == "__main__":
    engine = AdvisorEngine("patch_v1")
    
    # Test execution queries
    engine.process_query("Clock tower me kya map change hua?")
    engine.process_query("Chrono aur Wukong me kya nerf aaya?")
