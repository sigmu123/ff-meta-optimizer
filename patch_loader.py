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

    def _ingest_skills(self, data, file_name):
        # Handle Actives
        if "active" in file_name.lower() or "characters" in file_name.lower():
            items = data.get("active_skills", data.get("character_adjustments", []))
            self._parse_and_store(items, self.active_skills, force_type="active")

        # Handle Passives
        if "passive" in file_name.lower() or "characters" in file_name.lower():
            items = data.get("passive_skills", data.get("updates", []))
            self._parse_and_store(items, self.passive_skills, force_type="passive")

    def _ingest_weapons(self, data, file_name):
        if "weapon" in file_name.lower() or "attributes" in file_name.lower():
            items = data.get("weapons", data.get("weapon_balances", []))
            self._parse_and_store(items, self.weapons)

    def _parse_and_store(self, items, target_dict, force_type=None):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    key = item.get("character_id") or item.get("weapon_id") or item.get("name")
                    if key:
                        if force_type and item.get("type", "").lower() != force_type and force_type not in item.get("type", "").lower():
                            continue # Basic strict filtering
                        target_dict[str(key).lower()] = item
        elif isinstance(items, dict):
            for k, v in items.items():
                if isinstance(v, dict):
                    target_dict[str(k).lower()] = v
