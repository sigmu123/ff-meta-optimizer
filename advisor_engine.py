import sys
import os
from core.ttk_calculator import MechanicsEngine
from interface.prompt_parser import TacticalParser
from patch_loader import PatchDataLoader

class AdvisorEngine:
    def __init__(self, patch_version="patch_rampage"):
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
            
            # Smart root extraction for all patch variants
            char_root = data.get("characters", data)
            if isinstance(char_root, dict) and "character_adjustments" in char_root:
                char_root = char_root["character_adjustments"]
                
            found_any = False
            
            # 1. Actives Check
            actives = char_root.get("active_skills", char_root.get("actives", {}))
            if isinstance(actives, dict) and "active_skills" in actives:
                actives = actives["active_skills"]
            if isinstance(actives, dict) and "actives" in actives:
                actives = actives["actives"]
                
            if isinstance(actives, dict) and actives:
                for c_id, c_info in actives.items():
                    if isinstance(c_info, dict):
                        print(f" -> Active Skill: {c_id.upper()} | Skill: {c_info.get('skill_name', c_info.get('name', 'N/A'))} | Type: {c_info.get('type', 'active')}")
                        found_any = True
            elif isinstance(actives, list) and actives:
                for c in actives:
                    if isinstance(c, dict):
                        print(f" -> Active Skill: {c.get('character_id', c.get('name', '')).upper()} | Skill: {c.get('skill_name', 'N/A')} | Type: {c.get('type', 'active')}")
                        found_any = True

            # 2. Passives Check
            passives = char_root.get("passive_skills", char_root.get("passives", {}))
            if isinstance(passives, dict) and "passive_skills" in passives:
                passives = passives["passive_skills"]
            if isinstance(passives, dict) and "passives" in passives:
                passives = passives["passives"]
                
            if isinstance(passives, dict) and passives:
                for c_id, c_info in passives.items():
                    if isinstance(c_info, dict):
                        print(f" -> Passive Skill: {c_id.upper()} | Skill: {c_info.get('skill_name', c_info.get('name', 'N/A'))}")
                        found_any = True
            elif isinstance(passives, list) and passives:
                for p in passives:
                    if isinstance(p, dict):
                        print(f" -> Passive Skill: {p.get('character_id', p.get('name', '')).upper()} | Skill: {p.get('skill_name', 'N/A')}")
                        found_any = True

            # 3. Direct Character Array Fallback (agar data normal list array me ho)
            if not found_any:
                char_list = char_root if isinstance(char_root, list) else char_root.get("characters", char_root.get("character_list", []))
                if isinstance(char_list, list):
                    for c in char_list:
                        if isinstance(c, dict):
                            print(f" -> Character: {c.get('name', c.get('character_id', 'N/A')).upper()} | Skill: {c.get('skill_name', c.get('ability', 'N/A'))}")

        elif cat == "modes_and_maps":
            print("MAP & MODE MODIFICATIONS DETECTED:")
            
            mm_root = data.get("modes_and_maps", data)
            
            cs_econ = mm_root.get("clash_squad_economy", mm_root.get("clash_squad", {}))
            if cs_econ:
                print(f" -> CS Economy Updated: Armor/Helmet Upgrades Configured.")
                
            vending = mm_root.get("loot_and_vending", mm_root.get("vending_machine", {}))
            if isinstance(vending, dict) and vending:
                v_info = vending.get("vending_machine", vending)
                print(f" -> Vending Machine: Added {v_info.get('added_items', 'N/A')} | Removed {v_info.get('removed_items', 'N/A')}")

        elif cat == "system_and_settings":
            print("SYSTEM & QUALITY OF LIFE UPDATES DETECTED:")
            print(" -> Configured utilities and core mechanics dynamic check active.")

        else:
            print("[INFO]: No direct patch adjustments found for this specific query.")

if __name__ == "__main__":
    patches_dir = os.path.join("data", "patches")
    
    if os.path.exists(patches_dir):
        # Scan all patch folders inside data/patches automatically
        available_patches = [
            f for f in os.listdir(patches_dir) 
            if os.path.isdir(os.path.join(patches_dir, f))
        ]
        
        print(f"FOUND {len(available_patches)} PATCHES IN REPO: {available_patches}\n")
        
        # Test each patch dynamically
        for patch in available_patches:
            print("=" * 60)
            print(f"TESTING PATCH: {patch}")
            print("=" * 60)
            try:
                engine = AdvisorEngine(patch)
                engine.process_query("Kenta aur M24 me kya stats hain?")
                engine.process_query("A124 aur Steffie ke skill changes batao?")
                engine.process_query("Clash Squad aur vending machine me kya update hai?")
                print(f"\n[SUCCESS]: '{patch}' successfully loaded and verified!")
            except Exception as e:
                print(f"\n[ERROR IN {patch}]: {e}")
    else:
        print(f"[ERROR]: Directory '{patches_dir}' not found.")
