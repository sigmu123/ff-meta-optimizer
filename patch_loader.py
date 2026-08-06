import os
import json

class PatchLoader:
    def __init__(self, patch_name="patch_v33_heroes_arise"):
        self.patch_name = patch_name
        self.patch_dir = os.path.join("data", "patches", self.patch_name)
        self.manifest_path = os.path.join(self.patch_dir, "patch_manifest.json")
        
        self.manifest = self._load_json_safe(self.manifest_path)
        
        self.active_skills = {}
        self.passive_skills = {}
        self.characters = {}
        self.weapons = {}
        self.range_decay = {}
        self.modes_and_maps = {}
        self.utilities = {}
        
        self._load_all_data()

    def _load_json_safe(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _load_all_data(self):
        files = self.manifest.get("files", {}) if isinstance(self.manifest, dict) else {}
        
        if "active_skills" in files:
            self.active_skills = self._load_json_safe(os.path.join(self.patch_dir, files["active_skills"]))
        if "passive_skills" in files:
            self.passive_skills = self._load_json_safe(os.path.join(self.patch_dir, files["passive_skills"]))
        if "base_attributes" in files:
            self.weapons = self._load_json_safe(os.path.join(self.patch_dir, files["base_attributes"]))
        if "range_decay" in files:
            self.range_decay = self._load_json_safe(os.path.join(self.patch_dir, files["range_decay"]))

        if os.path.exists(self.patch_dir):
            for root, _, files_in_dir in os.walk(self.patch_dir):
                for file_name in files_in_dir:
                    if file_name.endswith(".json") and file_name != "patch_manifest.json":
                        file_path = os.path.join(root, file_name)
                        content = self._load_json_safe(file_path)
                        
                        if file_name in ["characters.json", "skills_rework.json"]:
                            self.characters = content
                        elif file_name == "active_skills.json":
                            self.active_skills = content
                        elif file_name == "passive_skills.json":
                            self.passive_skills = content
                                
                        elif file_name in ["weapons.json", "weapon_balance.json", "base_attributes.json"]:
                            if not self.weapons:
                                self.weapons = content
                                
                        elif file_name in ["modes_and_maps.json", "mode_adjustments.json", "gameplay_rules.json", "system_updates.json", "utilities.json"]:
                            if not self.modes_and_maps:
                                self.modes_and_maps = content
                            if not self.utilities:
                                self.utilities = content
