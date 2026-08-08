import os
import json

class PatchLoader:
    def __init__(self, patch_name="all", base_dir=None):
        self.patch_name = patch_name
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.patches_base_dir = os.path.join(base_dir, "data", "patches")
        
        self.active_skills = {}
        self.passive_skills = {}
        self.weapons = {}
        self.pets = []
        self.loadouts = []
        
        self._load_all_data()

    def _load_json_safe(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] Error reading JSON: {path} - {e}")
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
                    
                    file_path = os.path.join(root, file_name)
                    data = self._load_json_safe(file_path)
                    if not data:
                        continue

                    self._ingest_skills(data)
                    self._ingest_weapons(data)
                    self._ingest_pets_loadouts(data)

    def _ingest_skills(self, data):
        # Safely route active skills
        actives = data.get("active_skills", [])
        if "character_balance_numeric_changes" in data:
            actives = data["character_balance_numeric_changes"].get("active_skills", actives)
        self._parse_and_store(actives, self.active_skills)

        # Safely route passive skills
        passives = data.get("passive_skills", [])
        if "character_balance_numeric_changes" in data:
            passives = data["character_balance_numeric_changes"].get("passive_skills", passives)
        self._parse_and_store(passives, self.passive_skills)

        # Handle flat reworks to prevent active/passive corruption
        reworks = data.get("reworked_characters", data.get("character_reworks", data.get("character_balance_changes", [])))
        self._parse_and_store(reworks, self.passive_skills) # Defaulting reworks to passives to prevent active override

    def _ingest_weapons(self, data):
        # Enable recursive extraction for nested categories like 'assault_rifles'
        weapons_data = data.get("weapons", data.get("weapon_balances", data.get("weapon_adjustments", {})))
        self._parse_and_store(weapons_data, self.weapons, recursive=True)
        
    def _ingest_pets_loadouts(self, data):
        for key in ["pets", "pet_updates"]:
            if key in data:
                self._extract_list_names(data[key], self.pets, key="pet")
        
        if "loadouts" in data:
            if isinstance(data["loadouts"], dict):
                self.loadouts.extend(list(data["loadouts"].keys()))
            elif isinstance(data["loadouts"], list):
                self._extract_list_names(data["loadouts"], self.loadouts, key="name")

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

    def _parse_and_store(self, items, target_dict, recursive=False):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    key = item.get("character_id") or item.get("weapon_id") or item.get("name") or item.get("character") or item.get("weapon")
                    if key:
                        target_dict[str(key).lower()] = item
                        
        elif isinstance(items, dict):
            for k, v in items.items():
                if isinstance(v, dict):
                    # Recursive check for nested categories like {"smg": {"mp40": {...}}}
                    if recursive and any(isinstance(sub_v, dict) for sub_v in v.values()):
                        for sub_k, sub_v in v.items():
                            if isinstance(sub_v, dict):
                                target_dict[str(sub_k).lower()] = sub_v
                    else:
                        target_dict[str(k).lower()] = v
