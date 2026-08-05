import sys
import os
from core.ttk_calculator import MechanicsEngine
from interface.prompt_parser import TacticalParser
from patch_loader import PatchDataLoader

class AdvisorEngine:
    def __init__(self, patch_version="patch_rampage_2022"):
        self.patch_version = patch_version
        self.patch_path = os.path.join("data", "patches", self.patch_version)
        
        # Load raw JSON patch data dynamically
        self.loader = PatchDataLoader(self.patch_path)
        
        # Pass loaded patch version to parser engine
        self.parser = TacticalParser(self.patch_version)
        
    def process_query(self, query):
        parsed = self.parser.query_system(query)
        cat = parsed.get("category", "")
        data = parsed.get("data", {})
        
        print(f"\n[QUERY RECEIVED]: '{query}'")
        print(f"[TACTICAL CATEGORY]: {cat.upper()}")
        print("-" * 50)
        
        if cat == "weapons_and_items":
            print("ITEMS & WEAPON ADJUSTMENTS DETECTED:")
            
            # Base Attributes / New Weapons Handling
            base_data = data.get("base_attributes", {})
            new_weapons = base_data.get("new_weapons", base_data.get("weapons", {}))
            
            if isinstance(new_weapons, dict):
                for w_name, w_info in new_weapons.items():
                    print(f" -> New Weapon: {w_name} | Class: {w_info.get('category', 'N/A')} | Base Dmg: {w_info.get('base_damage', 'N/A')}")
            elif isinstance(new_weapons, list):
                for w in new_weapons:
                    print(f" -> Weapon: {w.get('weapon_name', w.get('weapon_id'))} | Class: {w.get('category')} | Base Dmg: {w.get('base_damage')}")

            # Weapon Adjustments Handling
            adj_data = data.get("weapon_adjustments", {}).get("weapon_modifications", {})
            if isinstance(adj_data, dict):
                for w_name, mods in adj_data.items():
                    print(f" -> Modification: {w_name} | Stats Adjusted: {list(mods.keys())}")

            # Range Decay Profiles
            decay_list = data.get("range_decay", {}).get("weapon_decay_profiles", [])
            for r in decay_list:
                print(f" -> Range Decay Profile: {r.get('weapon_id')} | Eff. Range: {r.get('effective_range_meters')}m | Max Range: {r.get('max_range_meters')}m")

        elif cat == "characters":
            print("CHARACTER SKILL ADJUSTMENTS DETECTED:")
            
            # Actives Parsing
            actives = data.get("active_skills", {}).get("actives", data.get("active_skills", {}).get("active_skills", {}))
            if isinstance(actives, dict):
                for c_id, c_info in actives.items():
                    print(f" -> Active Skill: {c_id.upper()} | Skill: {c_info.get('skill_name')} | Type: {c_info.get('type')}")
            elif isinstance(actives, list):
                for c in actives:
                    print(f" -> Active Skill: {c.get('character_id', '').upper()} | Skill: {c.get('skill_name')} | Type: {c.get('type')}")

            # Passives Parsing
            passives = data.get("passive_skills", {}).get("passives", data.get("passive_skills", {}).get("passive_skills", {}))
            if isinstance(passives, dict):
                for c_id, c_info in passives.items():
                    print(f" -> Passive Skill: {c_id.upper()} | Skill: {c_info.get('skill_name')}")
            elif isinstance(passives, list):
                for p in passives:
                    print(f" -> Passive Skill: {p.get('character_id', '').upper()} | Skill: {p.get('skill_name')}")

        elif cat == "modes_and_maps":
            print("MAP & MODE MODIFICATIONS DETECTED:")
            
            cs_econ = data.get("clash_squad_economy", {})
            if cs_econ:
                print(f" -> CS Economy Updated: Armor/Helmet Upgrades Configured.")
                
            vending = data.get("loot_and_vending", {}).get("vending_machine", {})
            if vending:
                print(f" -> Vending Machine: Added {vending.get('added_items')} | Removed {vending.get('removed_items')}")

        elif cat == "system_and_settings":
            print("SYSTEM & QUALITY OF LIFE UPDATES DETECTED:")
            print(" -> Configured utilities and core mechanics dynamic check active.")

        else:
            print("[INFO]: No direct patch adjustments found for this specific query.")

if __name__ == "__main__":
    # Pointing to the active Rampage 2022 patch directory
    engine = AdvisorEngine("patch_rampage_2022")
    
    # Rampage 2022 Tactical Test Queries
    engine.process_query("Kenta aur M24 me kya stats hain?")
    engine.process_query("A124 aur Steffie ke skill changes batao?")
    engine.process_query("Clash Squad aur vending machine me kya update hai?")
