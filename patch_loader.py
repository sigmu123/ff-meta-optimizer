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
        if not os.path.exists(self.patch_dir):
            return

        for root, _, files in os.walk(self.patch_dir):
            for file_name in files:
                if file_name == "patch_manifest.json" or not file_name.endswith(".json"):
                    continue
                
                file_path = os.path.join(root, file_name)
                data = self._load_json_safe(file_path)
                
                if file_name == "active_skills.json":
                    skill_list = data.get("active_skills", []) if isinstance(data, dict) else data
                    if isinstance(skill_list, list):
                        for skill in skill_list:
                            s_id = skill.get("character_id") or skill.get("character_name") or skill.get("skill_name") or skill.get("id")
                            if s_id:
                                self.active_skills[str(s_id).lower()] = skill
                    elif isinstance(data, dict):
                        for k, v in data.items():
                            if isinstance(v, dict):
                                self.active_skills[str(k).lower()] = v

                elif file_name == "passive_skills.json":
                    skill_list = data.get("passive_skills", []) if isinstance(data, dict) else data
                    if isinstance(skill_list, list):
                        for skill in skill_list:
                            s_id = skill.get("character_id") or skill.get("character_name") or skill.get("skill_name") or skill.get("id")
                            if s_id:
                                self.passive_skills[str(s_id).lower()] = skill
                    elif isinstance(data, dict):
                        for k, v in data.items():
                            if isinstance(v, dict):
                                self.passive_skills[str(k).lower()] = v

                elif file_name in ["characters.json", "skills_rework.json"]:
                    if isinstance(data, dict):
                        char_list = data.get("character_adjustments", []) or data.get("updates", [])
                        if isinstance(char_list, list):
                            for c in char_list:
                                c_id = c.get("character_id") or c.get("character_name") or c.get("id") or c.get("name")
                                if c_id:
                                    self.characters[str(c_id).lower()] = c
                        else:
                            self.characters.update(data)

                elif file_name in ["base_attributes.json", "weapons.json", "weapon_balance.json", "weapon_adjustments.json"]:
                    w_list = data.get("weapons", []) if isinstance(data, dict) else []
                    if isinstance(w_list, list) and len(w_list) > 0:
                        for w in w_list:
                            if isinstance(w, dict):
                                w_id = w.get("weapon_id") or w.get("name") or w.get("weapon_name")
                                if w_id:
                                    self.weapons[str(w_id).lower()] = w
                    elif isinstance(data, dict):
                        for k, v in data.items():
                            if k not in ["patch_version", "patch_date", "category", "special_weapon_mechanics", "global_weapon_mechanics", "weapon_tier_system", "global_weapon_mechanics"]:
                                if isinstance(v, dict):
                                    self.weapons[str(k).lower()] = v

                elif file_name == "range_decay.json":
                    if isinstance(data, dict):
                        self.range_decay.update(data)

                elif file_name in ["map_tactics.json", "modes_and_maps.json", "mode_adjustments.json", "gameplay_rules.json"]:
                    if isinstance(data, dict):
                        self.modes_and_maps.update(data)

                elif file_name in ["utilities.json", "system_updates.json", "system_qol.json"]:
                    if isinstance(data, dict):
                        self.utilities.update(data)

        if not self.characters.get("characters"):
            self.characters["characters"] = {**self.active_skills, **self.passive_skills}
