import os
import json
import logging
from collections import defaultdict
import re

class PatchLoader:
    def __init__(self, patch_name="all", base_dir=None, cumulative=True):
        self.patch_name = patch_name
        self.cumulative = cumulative
        base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.patches_base_dir = os.path.join(base_dir, "data", "patches")

        self.active_skills = {}
        self.passive_skills = {}
        self.weapons = {}
        self.pets = []
        self.loadouts = []

        self.character_adjustments = {}
        self.weapon_adjustments = {}

        logging.basicConfig(level=logging.WARNING)
        self._load_all_data()

        print(f"[DEBUG] Total weapons loaded: {len(self.weapons)}")
        print(f"[DEBUG] Total active skills loaded: {len(self.active_skills)}")
        print(f"[DEBUG] Total passive skills loaded: {len(self.passive_skills)}")
        print(f"[DEBUG] Pets: {self.pets}")
        print(f"[DEBUG] Loadouts: {self.loadouts}")

        if len(self.weapons) == 0 and len(self.active_skills) == 0:
            print("[WARNING] No data loaded. Trying fallback to patch_ob54 only.")
            self.cumulative = False
            self.patch_name = "patch_ob54"
            self.active_skills = {}
            self.passive_skills = {}
            self.weapons = {}
            self.pets = []
            self.loadouts = []
            self._load_all_data()
            print(f"[DEBUG] Fallback: weapons={len(self.weapons)}, actives={len(self.active_skills)}")

    def _load_json_safe(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"JSON Parse Error in {path}: {str(e)}")
        return {}

    def _get_sorted_patches(self):
        if not os.path.exists(self.patches_base_dir):
            return []
        folders = [f for f in os.listdir(self.patches_base_dir)
                   if os.path.isdir(os.path.join(self.patches_base_dir, f)) and f.startswith("patch_")]
        def sort_key(f):
            if "ob" in f:
                num = int(re.search(r'ob(\d+)', f).group(1)) if re.search(r'ob(\d+)', f) else 0
                return (2, num)
            else:
                return (1, f)
        return sorted(folders, key=sort_key)

    def _load_all_data(self):
        if self.cumulative:
            patch_folders = self._get_sorted_patches()
            print(f"[DEBUG] Cumulative patches to load: {patch_folders}")
            for patch_folder in patch_folders:
                self._load_patch(patch_folder)
        else:
            if self.patch_name == "all":
                patch_folders = self._get_sorted_patches()
                for patch_folder in patch_folders:
                    self._load_patch(patch_folder)
            else:
                print(f"[DEBUG] Loading single patch: {self.patch_name}")
                self._load_patch(self.patch_name)

    def _load_patch(self, patch_folder):
        patch_dir = os.path.join(self.patches_base_dir, patch_folder)
        if not os.path.isdir(patch_dir):
            return
        for root, _, files in os.walk(patch_dir):
            for file_name in files:
                if not file_name.endswith(".json") or file_name == "patch_manifest.json":
                    continue
                data = self._load_json_safe(os.path.join(root, file_name))
                if not data:
                    continue
                self._parse_generic_data(data, patch_folder)

    def _parse_generic_data(self, data, patch_ns):
        # ---- Characters & Skills ----
        char_lists = [
            "character_adjustments",
            "character_balance_changes",
            "reworked_characters",
            "character_reworks",
            "new_characters",
            "awakened_characters",
            "character_buffs",
            "character_nerfs"
        ]
        for key in char_lists:
            items = data.get(key, [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        self._extract_character_skill(item, patch_ns, override=True)

        if "active_skills" in data:
            self._parse_and_store(data["active_skills"], self.active_skills, patch_ns, key_field="name", override=True)
        if "passive_skills" in data:
            self._parse_and_store(data["passive_skills"], self.passive_skills, patch_ns, key_field="name", override=True)

        # ---- Weapons ----
        weapon_lists = [
            "weapon_adjustments",
            "weapon_balances",
            "weapons",
            "rifles",
            "smg",
            "shotguns",
            "pistols",
            "machine_guns",
            "others"
        ]
        for key in weapon_lists:
            items = data.get(key, [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        self._extract_weapon(item, patch_ns, override=True)
            elif isinstance(items, dict):
                for k, v in items.items():
                    if isinstance(v, dict):
                        self._extract_weapon(v, patch_ns, weapon_id=k, override=True)

        # ---- Pets ----
        pets_data = data.get("pets", []) or data.get("pet_updates", []) or data.get("new_pets", [])
        if pets_data:
            if isinstance(pets_data, list):
                for p in pets_data:
                    if isinstance(p, dict):
                        name = p.get("pet_name") or p.get("name") or p.get("pet")
                        if name and name not in self.pets:
                            self.pets.append(name)
            elif isinstance(pets_data, dict):
                for k in pets_data.keys():
                    if k not in self.pets:
                        self.pets.append(k)

        # ---- Loadouts (NEW: recursive extraction) ----
        self._extract_loadouts_recursive(data)

    # -------------------- NEW RECURSIVE LOADOUT EXTRACTOR --------------------
    def _extract_loadouts_recursive(self, data):
        """گہرائی میں جا کر تمام 'loadouts' کلیدوں کو ڈھونڈتا ہے۔"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "loadouts":
                    self._process_loadouts_data(value)
                elif isinstance(value, dict):
                    self._extract_loadouts_recursive(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._extract_loadouts_recursive(item)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._extract_loadouts_recursive(item)

    def _process_loadouts_data(self, loadouts_data):
        """لوڈ آؤٹ ڈیٹا (لسٹ یا ڈکشنری) کو پروسیس کر کے ناموں کو self.loadouts میں شامل کرتا ہے۔"""
        if isinstance(loadouts_data, list):
            for item in loadouts_data:
                if isinstance(item, dict):
                    name = item.get("name") or item.get("loadout_name")
                    if name and name not in self.loadouts:
                        self.loadouts.append(name)
        elif isinstance(loadouts_data, dict):
            for key in loadouts_data.keys():
                if key not in self.loadouts:
                    self.loadouts.append(key)
    # -----------------------------------------------------------------------

    def _extract_character_skill(self, item, patch_ns, override=True):
        char_name = item.get("character_name") or item.get("name") or item.get("character")
        if not char_name:
            return

        skill_name = item.get("skill_name") or item.get("skill") or ""
        skill_type = item.get("type") or item.get("skill_type") or ""

        is_active = False
        if skill_type:
            if "active" in skill_type.lower():
                is_active = True
            elif "passive" in skill_type.lower():
                is_active = False
            else:
                if "cooldown_seconds" in item or "duration_seconds" in item:
                    is_active = True
                else:
                    is_active = False

        skill_entry = {
            "character_name": char_name,
            "skill_name": skill_name,
            "type": "active" if is_active else "passive",
            "cooldown": item.get("cooldown_seconds") or item.get("cooldown"),
            "duration": item.get("duration_seconds") or item.get("duration"),
            "shield_hp": item.get("shield_hp"),
            "damage": item.get("damage"),
            "heal": item.get("heal"),
            "adjustments": {k: v for k, v in item.items() if k not in ["character_name", "skill_name", "type", "skill_type"]}
        }
        skill_entry = {k: v for k, v in skill_entry.items() if v is not None}

        target = self.active_skills if is_active else self.passive_skills
        key = char_name.lower()

        if override:
            target[key] = skill_entry
        else:
            if key not in target:
                target[key] = skill_entry

        if char_name not in self.character_adjustments:
            self.character_adjustments[char_name] = []
        self.character_adjustments[char_name].append(item)

    def _extract_weapon(self, item, patch_ns, weapon_id=None, override=True):
        wep_name = item.get("weapon_name") or item.get("name") or weapon_id
        if not wep_name:
            return

        stats = {
            "damage": item.get("damage") or item.get("base_damage"),
            "rate_of_fire": item.get("rate_of_fire") or item.get("fire_rate"),
            "armor_penetration": item.get("armor_penetration") or item.get("armor_pen"),
            "range": item.get("range") or item.get("effective_range"),
            "magazine": item.get("magazine_capacity") or item.get("clip_size"),
            "adjustments": {k: v for k, v in item.items() if k not in ["weapon_name", "name", "damage", "rate_of_fire", "armor_penetration", "range", "magazine_capacity"]}
        }
        stats = {k: v for k, v in stats.items() if v is not None}

        key = wep_name.lower()
        if override:
            self.weapons[key] = stats
        else:
            if key not in self.weapons:
                self.weapons[key] = stats

        if wep_name not in self.weapon_adjustments:
            self.weapon_adjustments[wep_name] = []
        self.weapon_adjustments[wep_name].append(item)

    def _parse_and_store(self, items, target_dict, patch_ns, key_field="name", override=True):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    key = item.get(key_field) or item.get("character_id") or item.get("weapon_id")
                    if key:
                        key = key.lower()
                        if override:
                            target_dict[key] = item
                        else:
                            if key not in target_dict:
                                target_dict[key] = item
        elif isinstance(items, dict):
            for k, v in items.items():
                if isinstance(v, dict):
                    key = k.lower()
                    if override:
                        target_dict[key] = v
                    else:
                        if key not in target_dict:
                            target_dict[key] = v
