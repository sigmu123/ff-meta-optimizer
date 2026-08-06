import os
import json

class PatchDataLoader:
    def __init__(self, patch_dir):
        self.patch_dir = patch_dir
        self.manifest = self._load_json_safe(os.path.join(patch_dir, "patch_manifest.json"))
        
        self.active_skills = {}
        self.passive_skills = {}
        self.synergies = {}
        self.weapons = {}
        self.range_decay = {}
        self.utilities = {}
        self.characters = {}
        
        self._load_all_data()

    def _load_json_safe(self, file_path):
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _load_all_data(self):
        # 1. Manifest specific files check
        files = self.manifest.get("files", {}) if isinstance(self.manifest, dict) else {}
        
        if "active_skills" in files:
            self.active_skills = self._load_json_safe(os.path.join(self.patch_dir, files["active_skills"]))
        if "passive_skills" in files:
            self.passive_skills = self._load_json_safe(os.path.join(self.patch_dir, files["passive_skills"]))
        if "base_attributes" in files:
            self.weapons = self._load_json_safe(os.path.join(self.patch_dir, files["base_attributes"]))
        if "range_decay" in files:
            self.range_decay = self._load_json_safe(os.path.join(self.patch_dir, files["range_decay"]))

        # 2. Universal File Scanner (for patches having characters.json, modes_and_maps.json, etc.)
        if os.path.exists(self.patch_dir):
            for file_name in os.listdir(self.patch_dir):
                if file_name.endswith(".json"):
                    file_path = os.path.join(self.patch_dir, file_name)
                    content = self._load_json_safe(file_path)
                    
                    if file_name == "characters.json":
                        self.characters = content
                        if not self.active_skills:
                            self.active_skills = content
                        if not self.passive_skills:
                            self.passive_skills = content
                    elif file_name == "weapons.json" and not self.weapons:
                        self.weapons = content
                    elif file_name == "modes_and_maps.json":
                        setattr(self, "modes_and_maps", content)
