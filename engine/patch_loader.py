import os
import json

class PatchDataLoader:
    def __init__(self, patch_dir):
        self.patch_dir = patch_dir
        self.manifest = self._load_json(os.path.join(patch_dir, "patch_manifest.json"))
        self.active_skills = {}
        self.passive_skills = {}
        self.weapons = {}
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
            path = os.path.join(self.patch_dir, files["active_skills"])
            self.active_skills = self._load_json(path)

        if "passive_skills" in files:
            path = os.path.join(self.patch_dir, files["passive_skills"])
            self.passive_skills = self._load_json(path)

        if "base_attributes" in files:
            path = os.path.join(self.patch_dir, files["base_attributes"])
            self.weapons = self._load_json(path)

        if "utilities" in files:
            path = os.path.join(self.patch_dir, files["utilities"])
            self.utilities = self._load_json(path)

    def get_character_active_skill(self, character_id):
        skills = self.active_skills.get("active_skills", [])
        return next((s for s in skills if s.get("character_id") == character_id.lower()), None)

    def get_weapon_stats(self, weapon_id):
        weapons = self.weapons.get("weapons", [])
        return next((w for w in weapons if w.get("weapon_id") == weapon_id.lower()), None)

if __name__ == "__main__":
    # Quick Local Test Check
    loader = PatchDataLoader("data/patches/patch_v33_heroes_arise")
    print("Loaded Patch:", loader.manifest.get("patch_id"))
    print("Kenta Skill Test:", loader.get_character_active_skill("kenta"))
