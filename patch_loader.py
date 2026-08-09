import os
import json
import logging

class PatchLoader:
    def __init__(self, patch_name="all", base_dir=None):
        self.patch_name = patch_name
        base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.patches_base_dir = os.path.join(base_dir, "data", "patches")
        
        self.active_skills = {}
        self.passive_skills = {}
        self.weapons = {}
        self.pets = []
        self.loadouts = []
        
        logging.basicConfig(level=logging.WARNING)
        self._load_all_data()

    def _load_json_safe(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"JSON Parse Error in {path}: {str(e)}")
        return {}

    def _load_all_data(self):
        if not os.path.exists(self.patches_base_dir): 
            return

        patch_folders = sorted(os.listdir(self.patches_base_dir))
        if self.patch_name != "all" and self.patch_name in patch_folders:
            patch_folders = [self.patch_name]

        for patch_folder in patch_folders:
            patch_dir = os.path.join(self.patches_base_dir, patch_folder)
            if not os.path.isdir(patch_dir): 
                continue
                
            for root, _, files in os.walk(patch_dir):
                for file_name in files:
                    if not file_name.endswith(".json") or file_name == "patch_manifest.json":
                        continue
                    
                    data = self._load_json_safe(os.path.join(root, file_name))
                    if not data: 
                        continue

                    self._ingest_skills(data, patch_folder)
                    self._ingest_weapons(data, patch_folder)
                    self._ingest_pets_loadouts(data)

    def _ingest_skills(self, data, patch_ns):
        actives = data.get("active_skills", [])
        if "character_balance_numeric_changes" in data:
            actives = data["character_balance_numeric_changes"].get("active_skills", actives)
        self._parse_and_store(actives, self.active_skills, patch_ns)

        passives = data.get("passive_skills", [])
        if "character_balance_numeric_changes" in data:
            passives = data["character_balance_numeric_changes"].get("passive_skills", passives)
        self._parse_and_store(passives, self.passive_skills, patch_ns)

        mixed_skills = []
        for key in ["reworked_characters", "character_reworks", "character_balance_changes", "new_characters", "awakened_characters"]:
            val = data.get(key, {})
            if isinstance(val, list):
                mixed_skills.extend(val)
            elif isinstance(val, dict):
                mixed_skills.extend(val.values())
        
        for item in mixed_skills:
            if isinstance(item, dict):
                skill_info = item.get("skill") or item.get("original_skill") or item.get("changes") or item
                skill_type = str(skill_info.get("type", "")).lower() if isinstance(skill_info, dict) else ""
                
                is_active = "active" in skill_type or (isinstance(skill_info, dict) and ("duration" in skill_info or "cooldown" in skill_info))
                
                if is_active:
                    self._parse_and_store([item], self.active_skills, patch_ns)
                else:
                    self._parse_and_store([item], self.passive_skills, patch_ns)

    def _ingest_weapons(self, data, patch_ns):
        weapon_keys = ["weapons", "weapon_balances", "weapon_adjustments", "rifles", "smg", "shotguns", "pistols", "machine_guns", "others"]
        for key in weapon_keys:
            if key in data:
                self._parse_and_store(data[key], self.weapons, patch_ns, recursive=True)
        
    def _ingest_pets_loadouts(self, data):
        for key in ["pets", "pet_updates"]:
            if key in data: 
                self._extract_list_names(data.get(key, []), self.pets, key="pet")
        
        if "loadouts" in data:
            ld = data["loadouts"]
            if isinstance(ld, dict): 
                self.loadouts.extend(list(ld.keys()))
            elif isinstance(ld, list): 
                self._extract_list_names(ld, self.loadouts, key="name")

    def _extract_list_names(self, items, target_list, key="name"):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    val = item.get(key) or item.get("name")
                    if val and str(val).lower() not in [x.lower() for x in target_list]:
                        target_list.append(str(val))
        elif isinstance(items, dict):
            for k in items.keys():
                if str(k).lower() not in [x.lower() for x in target_list]: 
                    target_list.append(str(k))

    def _parse_and_store(self, items, target_dict, patch_ns, recursive=False):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    k = item.get("character_id") or item.get("weapon_id") or item.get("name") or item.get("character")
                    if k: 
                        target_dict[f"{patch_ns}_{str(k).lower()}"] = item
                        
        elif isinstance(items, dict):
            for k, v in items.items():
                if isinstance(v, dict):
                    if recursive and any(isinstance(sub_v, dict) for sub_v in v.values()):
                        for sub_k, sub_v in v.items():
                            if isinstance(sub_v, dict): 
                                target_dict[f"{patch_ns}_{str(sub_k).lower()}"] = sub_v
                    else:
                        target_dict[f"{patch_ns}_{str(k).lower()}"] = v
