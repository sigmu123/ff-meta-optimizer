import os
import json

class PatchLoader:
    def __init__(self, patch_name="patch_ob54", base_dir=None):
        self.patch_name = patch_name
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.patch_dir = os.path.join(base_dir, "data", "patches", self.patch_name)
        self.manifest_path = os.path.join(self.patch_dir, "patch_manifest.json")
        
        self.manifest = self._load_json_safe(self.manifest_path)
        
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
            except Exception:
                pass
        return {}

    def _load_all_data(self):
        if not os.path.exists(self.patch_dir):
            return

        for root, _, files in os.walk(self.patch_dir):
            for file_name in files:
                if not file_name.endswith(".json") or file_name == "patch_manifest.json":
                    continue
                
                file_path = os.path.join(root, file_name)
                data = self._load_json_safe(file_path)
                if not data:
                    continue

                self._ingest_skills(data, file_name)
                self._ingest_weapons(data, file_name)
                self._ingest_pets_loadouts(data, file_name)

    def _ingest_skills(self, data, file_name):
        # Handle Actives from multiple possible schema variations
        items = data.get("active_skills", data.get("character_adjustments", []))
        if not items and "character_balance_numeric_changes" in data:
            items = data["character_balance_numeric_changes"].get("active_skills", {})
        if not items and "new_characters" in data:
            items = data.get("new_characters", [])
        if not items and "awakened_characters" in data:
            items = data.get("awakened_characters", [])
        if not items and "character_reworks" in data:
            items = data.get("character_reworks", [])
            
        self._parse_and_store(items, self.active_skills, force_type="active")

        # Handle Passives from multiple possible schema variations
        p_items = data.get("passive_skills", data.get("updates", []))
        if not p_items and "character_balance_numeric_changes" in data:
            p_items = data["character_balance_numeric_changes"].get("passive_skills", {})
        if not p_items and "character_balance_changes" in data:
            p_items = data.get("character_balance_changes", [])
            
        self._parse_and_store(p_items, self.passive_skills, force_type="passive")

    def _ingest_weapons(self, data, file_name):
        # Handle deep nested categories in weapons like OB40 schema
        items = data.get("weapons", data.get("weapon_balances", []))
        if not items and "weapon_adjustments" in data:
            items = data.get("weapon_adjustments", {})
        self._parse_and_store(items, self.weapons)
        
    def _ingest_pets_loadouts(self, data, file_name):
        # Dynamically extract Pets
        if "pets" in data:
            self._extract_list_names(data["pets"], self.pets)
        if "pet_updates" in data:
            self._extract_list_names(data["pet_updates"], self.pets, key="pet")
        
        # Dynamically extract Loadouts
        if "loadouts" in data:
            if isinstance(data["loadouts"], dict):
                self.loadouts.extend(list(data["loadouts"].keys()))
            elif isinstance(data["loadouts"], list):
                self._extract_list_names(data["loadouts"], self.loadouts, key="name")

    def _extract_list_names(self, items, target_list, key="name"):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    val = item.get(key)
                    if val and str(val).lower() not in [x.lower() for x in target_list]:
                        target_list.append(str(val))
        elif isinstance(items, dict):
            for k in items.keys():
                if str(k).lower() not in [x.lower() for x in target_list]:
                    target_list.append(str(k))

    def _parse_and_store(self, items, target_dict, force_type=None):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    key = item.get("character_id") or item.get("weapon_id") or item.get("name") or item.get("character") or item.get("weapon")
                    if key:
                        target_dict[str(key).lower()] = item
                        
        elif isinstance(items, dict):
            for k, v in items.items():
                if isinstance(v, dict):
                    # Resolve nested categories (e.g., "smg": {"mp40": {...}})
                    if any(isinstance(sub_v, dict) for sub_v in v.values()):
                        for sub_k, sub_v in v.items():
                            if isinstance(sub_v, dict):
                                target_dict[str(sub_k).lower()] = sub_v
                    else:
                        target_dict[str(k).lower()] = v
