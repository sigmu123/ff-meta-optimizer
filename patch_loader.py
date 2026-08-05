import os
import json

class PatchDataLoader:
    def __init__(self, patch_dir):
        self.patch_dir = patch_dir
        self.manifest = self._load_json(os.path.join(patch_dir, "patch_manifest.json"))
        self.active_skills = {}
        self.passive_skills = {}
        self.synergies = {}
        self.weapons = {}
        self.range_decay = {}
        self.utilities = {}
        self._load_all_data()

    def _load_json(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_all_data(self):
        files = self.manifest.get("files", {})
        
        if "active_skills" in files:
            self.active_skills = self._load_json(os.path.join(self.patch_dir, files["active_skills"]))

        if "passive_skills" in files:
            self.passive_skills = self._load_json(os.path.join(self.patch_dir, files["passive_skills"]))

        if "synergies" in files:
            self.synergies = self._load_json(os.path.join(self.patch_dir, files["synergies"]))

        if "base_attributes" in files:
            self.weapons = self._load_json(os.path.join(self.patch_dir, files["base_attributes"]))

        if "range_decay" in files:
            self.range_decay = self._load_json(os.path.join(self.patch_dir, files["range_decay"]))

        if "utilities" in files:
            self.utilities = self._load_json(os.path.join(self.patch_dir, files["utilities"]))
