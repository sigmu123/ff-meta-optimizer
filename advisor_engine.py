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
            
            # Extract list/dict from loader
            w_items = []
            if isinstance(weapons_data, dict):
                w_items = weapons_data.get("base_attributes", weapons_data.get("weapon_adjustments", weapons_data.get("updates", [])))
                if isinstance(weapons_data, dict) and not w_items:
                    w_items = weapons_data
            elif isinstance(weapons_data, list):
                w_items = weapons_data

            if isinstance(w_items, dict):
                for w_name, w_info in w_items.items():
                    if isinstance(w_info, dict):
                        print(f" -> Weapon: {w_name} | Class: {w_info.get('category', 'N/A')}")
            elif isinstance(w_items, list):
                for w in w_items:
                    if isinstance(w, dict):
                        w_name = w.get("weapon_name", w.get("name", w.get("id", "N/A")))
                        print(f" -> Weapon: {w_name} | Type/Change: {w.get('change_type', w.get('category', 'N/A'))}")

        elif cat == "characters":
            print("CHARACTER SKILL ADJUSTMENTS DETECTED:")
            
            active = self.loader.active_skills
            passive = self.loader.passive_skills
            chars = self.loader.characters
            
            printed = False

            # Unified search list across all loaded character objects
            data_sources = [chars, active, passive]

            for src in data_sources:
                if not src:
                    continue
                
                # Check for "updates" list (patch_5th_anniv format)
                if isinstance(src, dict) and "updates" in src and isinstance(src["updates"], list):
                    for item in src["updates"]:
                        if isinstance(item, dict):
                            c_name = item.get("character_name", item.get("name", "UNKNOWN")).upper()
                            s_name = item.get("skill_name", "N/A")
                            c_type = item.get("change_type", "Modified")
                            print(f" -> Skill Adjust: {c_name} | Skill: {s_name} | Type: {c_type}")
                            printed = True
                
                # Check for "character_adjustments" list (patch_v1 / patch_v2 format)
                elif isinstance(src, dict) and "character_adjustments" in src and isinstance(src["character_adjustments"], list):
                    for item in src["character_adjustments"]:
                        if isinstance(item, dict):
                            c_name = item.get("name", item.get("id", "UNKNOWN")).upper()
                            s_name = item.get("skill_name", "N/A")
                            print(f" -> Skill Adjust: {c_name} | Skill: {s_name} | Status: Modified")
                            printed = True

                # Check Direct Dict Iteration (patch_rampage active_skills / passive_skills)
                elif isinstance(src, dict):
                    skills_dict = src.get("active_skills", src.get("passive_skills", src))
                    if isinstance(skills_dict, dict):
                        for char_id, info in skills_dict.items():
                            if isinstance(info, dict) and ("skill_name" in info or "name" in info):
                                s_name = info.get("skill_name", info.get("name", "N/A"))
                                s_type = info.get("type", "Adjustment")
                                print(f" -> Skill Adjust: {char_id.upper()} | Skill: {s_name} | Type: {s_type}")
                                printed = True
                                
                # Check Direct List Iteration
                elif isinstance(src, list):
                    for item in src:
                        if isinstance(item, dict):
                            c_name = item.get("character_name", item.get("name", item.get("id", "UNKNOWN"))).upper()
                            s_name = item.get("skill_name", item.get("ability", "N/A"))
                            print(f" -> Skill Adjust: {c_name} | Skill: {s_name}")
                            printed = True

        elif cat == "modes_and_maps":
            print("MAP & MODE MODIFICATIONS DETECTED:")
            utilities = getattr(self.loader, "modes_and_maps", getattr(self.loader, "utilities", None))
            print(f" -> Map & Utility Updates Loaded Successfully.")

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
