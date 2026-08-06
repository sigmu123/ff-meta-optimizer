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
        self.modes_and_maps = {}
        
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
        # 1. Manifest Specific Files Check
        files = self.manifest.get("files", {}) if isinstance(self.manifest, dict) else {}
        
        if "active_skills" in files:
            self.active_skills = self._load_json_safe(os.path.join(self.patch_dir, files["active_skills"]))
        if "passive_skills" in files:
            self.passive_skills = self._load_json_safe(os.path.join(self.patch_dir, files["passive_skills"]))
        if "base_attributes" in files:
            self.weapons = self._load_json_safe(os.path.join(self.patch_dir, files["base_attributes"]))
        if "range_decay" in files:
            self.range_decay = self._load_json_safe(os.path.join(self.patch_dir, files["range_decay"]))

        # 2. Recursive Sub-folder Scanner (os.walk for nested directories like characters/, weapons/, etc.)
        if os.path.exists(self.patch_dir):
            for root, _, files_in_dir in os.walk(self.patch_dir):
                for file_name in files_in_dir:
                    if file_name.endswith(".json") and file_name != "patch_manifest.json":
                        file_path = os.path.join(root, file_name)
                        content = self._load_json_safe(file_path)
                        
                        # Characters Data Mapping
                        if file_name in ["characters.json", "skills_rework.json", "active_skills.json", "passive_skills.json"]:
                            if not self.characters:
                                self.characters = content
                            if "active" in file_name and not self.active_skills:
                                self.active_skills = content
                            elif "passive" in file_name and not self.passive_skills:
                                self.passive_skills = content
                                
                        # Weapons Data Mapping
                        elif file_name in ["weapons.json", "weapon_balance.json", "base_attributes.json"]:
                            if not self.weapons:
                                self.weapons = content
                                
                        # Mechanics / Modes & Maps Mapping
                        elif file_name in ["modes_and_maps.json", "mode_adjustments.json", "gameplay_rules.json", "system_updates.json"]:
                            if not self.modes_and_maps:
                                self.modes_and_maps = content
                            if not self.utilities:
                                self.utilities = content
