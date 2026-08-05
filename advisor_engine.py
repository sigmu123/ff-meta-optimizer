import sys
import os
from core.ttk_calculator import MechanicsEngine
from interface.prompt_parser import TacticalParser
from patch_loader import PatchDataLoader

class AdvisorEngine:
    def __init__(self, patch_version="patch_v33_heroes_arise"):
        self.patch_version = patch_version
        self.patch_path = os.path.join("data", "patches", self.patch_version)
        
        # Load raw JSON patch data dynamically
        self.loader = PatchDataLoader(self.patch_path)
        
        # Pass loaded patch version to parser engine
        self.parser = TacticalParser(self.patch_version)
        
    def process_query(self, query):
        parsed = self.parser.query_system(query)
        cat = parsed["category"]
        data = parsed.get("data", {})
        
        print(f"\n[QUERY RECEIVED]: '{query}'")
        print(f"[TACTICAL CATEGORY]: {cat.upper()}")
        print("-" * 50)
        
        if cat == "weapons_and_items":
            print("ITEMS & WEAPON ADJUSTMENTS DETECTED:")
            base_list = data.get("base_attributes", {}).get("weapons", [])
            for w in base_list:
                print(f" -> Weapon: {w.get('weapon_name', w.get('weapon_id'))} | Class: {w.get('category')} | Base Dmg: {w.get('base_damage')}")
            decay_list = data.get("range_decay", {}).get("weapon_decay_profiles", [])
            for r in decay_list:
                print(f" -> Range Decay Profile: {r.get('weapon_id')} | Eff. Range: {r.get('effective_range_meters')}m | Max Range: {r.get('max_range_meters')}m")

        elif cat == "characters":
            print("CHARACTER SKILL ADJUSTMENTS DETECTED:")
            active_list = data.get("active_skills", {}).get("active_skills", [])
            passive_list = data.get("passive_skills", {}).get("passive_skills", [])
            for c in active_list:
                print(f" -> Active Skill: {c.get('character_id', '').upper()} | Skill: {c.get('skill_name')} | Type: {c.get('type')}")
            for p in passive_list:
                print(f" -> Passive Skill: {p.get('character_id', '').upper()} | Skill: {p.get('skill_name')}")

        elif cat == "modes_and_maps":
            print("MAP & MODE MODIFICATIONS DETECTED:")
            missions = data.get("in_game_missions", [])
            for m in missions:
                print(f" -> Mission: {m.get('mission_type')} | Target: {m.get('target', 'N/A')}")
            vending = data.get("vending_machine_adjustments", {})
            if vending:
                print(f" -> Vending Machine: {vending.get('description', 'Updated')}")

        elif cat == "system_and_settings":
            print("SYSTEM & QUALITY OF LIFE UPDATES DETECTED:")
            print(" -> Configured utilities and core mechanics dynamic check active.")

        else:
            print("[INFO]: No direct patch adjustments found for this specific query.")

if __name__ == "__main__":
    # Pointing to the active OB33 patch directory
    engine = AdvisorEngine("patch_v33_heroes_arise")
    
    # OB33 Tactical Test Execution Queries
    engine.process_query("Kenta aur G36 me kya stats hain?")
    engine.process_query("A124 aur Steffie ke skill changes batao?")
    engine.process_query("Clash Squad aur mission me kya update hai?")
