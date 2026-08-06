import sys
import os
from interface.prompt_parser import TacticalParser
from patch_loader import PatchDataLoader

class AdvisorEngine:
    def __init__(self, patch_version="patch_rampage"):
        self.patch_version = patch_version
        self.patch_path = os.path.join("data", "patches", self.patch_version)
        self.loader = PatchDataLoader(self.patch_path)
        self.parser = TacticalParser(self.patch_version)
        
    def process_query(self, query):
        parsed = self.parser.query_system(query)
        cat = parsed.get("category", "")
        
        print(f"\n[QUERY RECEIVED]: '{query}'")
        print(f"[TACTICAL CATEGORY]: {cat.upper()}")
        print("-" * 50)
        
        if cat == "weapons_and_items":
            print("ITEMS & WEAPON ADJUSTMENTS DETECTED:")
            weapons_data = self.loader.weapons
            
            if isinstance(weapons_data, dict):
                base_attrs = weapons_data.get("base_attributes", weapons_data.get("weapon_adjustments", weapons_data))
                if isinstance(base_attrs, dict):
                    for w_name, w_info in base_attrs.items():
                        if isinstance(w_info, dict):
                            print(f" -> Weapon: {w_name} | Class: {w_info.get('category', 'N/A')} | Base Dmg: {w_info.get('base_damage', 'N/A')}")
                elif isinstance(base_attrs, list):
                    for w in base_attrs:
                        if isinstance(w, dict):
                            print(f" -> Weapon: {w.get('name', w.get('weapon_name', 'N/A'))} | Class: {w.get('category', 'N/A')}")
            elif isinstance(weapons_data, list):
                for w in weapons_data:
                    if isinstance(w, dict):
                        print(f" -> Weapon: {w.get('weapon_name', w.get('name', 'N/A'))} | Class: {w.get('category', 'N/A')}")

        elif cat == "characters":
            print("CHARACTER SKILL ADJUSTMENTS DETECTED:")
            
            active = self.loader.active_skills
            passive = self.loader.passive_skills
            chars = self.loader.characters

            # 1. Inspect Wrapped Dict Format (e.g. {"character_adjustments": [...]})
            if isinstance(chars, dict) and "character_adjustments" in chars:
                for item in chars["character_adjustments"]:
                    if isinstance(item, dict):
                        c_name = item.get("name", item.get("id", "UNKNOWN")).upper()
                        s_name = item.get("skill_name", "N/A")
                        print(f" -> Skill Adjust: {c_name} | Skill: {s_name} | Status: Modified")

            # 2. Inspect Direct Key-Value Dictionary Format (e.g. {"alok": {"skill_name": ...}})
            elif isinstance(active, dict) and active:
                skills_dict = active.get("active_skills", active)
                if isinstance(skills_dict, dict):
                    for char_id, info in skills_dict.items():
                        if isinstance(info, dict) and "skill_name" in info:
                            s_name = info.get("skill_name", "N/A")
                            s_type = info.get("type", "active")
                            print(f" -> Active Skill: {char_id.upper()} | Skill: {s_name} | Type: {s_type}")

                if isinstance(passive, dict) and passive:
                    pass_dict = passive.get("passive_skills", passive)
                    if isinstance(pass_dict, dict):
                        for char_id, info in pass_dict.items():
                            if isinstance(info, dict) and "skill_name" in info:
                                s_name = info.get("skill_name", "N/A")
                                print(f" -> Passive Skill: {char_id.upper()} | Skill: {s_name}")

            # 3. Direct Flat List Format (e.g. [ {"name": ...}, ... ])
            else:
                raw_list = chars if isinstance(chars, list) else (active if isinstance(active, list) else [])
                if raw_list:
                    for item in raw_list:
                        if isinstance(item, dict):
                            c_name = item.get("name", item.get("character_id", item.get("id", "UNKNOWN"))).upper()
                            s_name = item.get("skill_name", item.get("ability", "N/A"))
                            s_type = item.get("type", "Adjustment")
                            print(f" -> Skill Adjust: {c_name} | Skill: {s_name} | Type: {s_type}")

        elif cat == "modes_and_maps":
            print("MAP & MODE MODIFICATIONS DETECTED:")
            utilities = getattr(self.loader, "modes_and_maps", self.loader.utilities)
            if utilities:
                print(f" -> Map & Utility Updates Loaded.")

if __name__ == "__main__":
    patches_dir = os.path.join("data", "patches")
    if os.path.exists(patches_dir):
        available_patches = [f for f in os.listdir(patches_dir) if os.path.isdir(os.path.join(patches_dir, f))]
        print(f"FOUND {len(available_patches)} PATCHES IN REPO: {available_patches}\n")
        
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
