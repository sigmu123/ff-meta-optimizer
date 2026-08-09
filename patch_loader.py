import os
import json
import logging
from collections import defaultdict

class PatchLoader:
    def __init__(self, patch_name="all", base_dir=None):
        self.patch_name = patch_name
        base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.patches_base_dir = os.path.join(base_dir, "data", "patches")

        # Stores parsed data per category
        self.active_skills = {}          # character_name -> skill dict
        self.passive_skills = {}         # character_name -> skill dict
        self.weapons = {}                # weapon_name -> stat dict
        self.pets = []                   # list of pet names
        self.loadouts = []               # list of loadout names

        # Additional storage for adjustments
        self.character_adjustments = {}  # character_name -> list of adjustments
        self.weapon_adjustments = {}     # weapon_name -> list of adjustments

        logging.basicConfig(level=logging.WARNING)
        self._load_all_data()

    def _load_json_safe(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"JSON Parse Error in {path}: {str(e)}")
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

                    data = self._load_json_safe(os.path.join(root, file_name))
                    if not data:
                        continue

                    self._parse_generic_data(data, patch_folder)

    def _parse_generic_data(self, data, patch_ns):
        """
        Intelligently extract skills, weapons, pets, loadouts from various JSON structures.
        """
        # ---- Characters & Skills ----
        # Look for known lists
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
                        self._extract_character_skill(item, patch_ns)

        # Also check for direct "active_skills" or "passive_skills" keys
        if "active_skills" in data:
            self._parse_and_store(data["active_skills"], self.active_skills, patch_ns, key_field="name")
        if "passive_skills" in data:
            self._parse_and_store(data["passive_skills"], self.passive_skills, patch_ns, key_field="name")

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
                        self._extract_weapon(item, patch_ns)
            elif isinstance(items, dict):
                # Some patches have nested dicts
                for k, v in items.items():
                    if isinstance(v, dict):
                        self._extract_weapon(v, patch_ns, weapon_id=k)

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

        # ---- Loadouts ----
        loadouts_data = data.get("loadouts", [])
        if loadouts_data:
            if isinstance(loadouts_data, list):
                for ld in loadouts_data:
                    if isinstance(ld, dict):
                        name = ld.get("name") or ld.get("loadout_name")
                        if name and name not in self.loadouts:
                            self.loadouts.append(name)
            elif isinstance(loadouts_data, dict):
                for k in loadouts_data.keys():
                    if k not in self.loadouts:
                        self.loadouts.append(k)

    def _extract_character_skill(self, item, patch_ns):
        """Extract active/passive skill info from a character adjustment item."""
        char_name = item.get("character_name") or item.get("name") or item.get("character")
        if not char_name:
            return

        skill_name = item.get("skill_name") or item.get("skill") or ""
        skill_type = item.get("type") or item.get("skill_type") or ""

        # Determine if active or passive
        is_active = False
        if skill_type:
            if "active" in skill_type.lower():
                is_active = True
            elif "passive" in skill_type.lower():
                is_active = False
            else:
                # heuristic: presence of cooldown/duration often means active
                if "cooldown_seconds" in item or "duration_seconds" in item:
                    is_active = True
                else:
                    is_active = False

        # Create a skill entry
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
        # Clean up None values
        skill_entry = {k: v for k, v in skill_entry.items() if v is not None}

        # Store in appropriate dictionary
        target = self.active_skills if is_active else self.passive_skills
        # Use character_name as key (with patch prefix to avoid collisions)
        key = f"{patch_ns}_{char_name.lower()}"
        target[key] = skill_entry

        # Also store adjustment separately for later use
        if char_name not in self.character_adjustments:
            self.character_adjustments[char_name] = []
        self.character_adjustments[char_name].append(item)

    def _extract_weapon(self, item, patch_ns, weapon_id=None):
        """Extract weapon stats from a weapon adjustment item."""
        wep_name = item.get("weapon_name") or item.get("name") or weapon_id
        if not wep_name:
            return

        # Build a stats dict
        stats = {
            "damage": item.get("damage") or item.get("base_damage"),
            "rate_of_fire": item.get("rate_of_fire") or item.get("fire_rate"),
            "armor_penetration": item.get("armor_penetration") or item.get("armor_pen"),
            "range": item.get("range") or item.get("effective_range"),
            "magazine": item.get("magazine_capacity") or item.get("clip_size"),
            "adjustments": {k: v for k, v in item.items() if k not in ["weapon_name", "name", "damage", "rate_of_fire", "armor_penetration", "range", "magazine_capacity"]}
        }
        # Clean
        stats = {k: v for k, v in stats.items() if v is not None}

        # Store
        key = f"{patch_ns}_{wep_name.lower()}"
        self.weapons[key] = stats

        # Also store adjustment separately
        if wep_name not in self.weapon_adjustments:
            self.weapon_adjustments[wep_name] = []
        self.weapon_adjustments[wep_name].append(item)

    def _parse_and_store(self, items, target_dict, patch_ns, key_field="name"):
        """Generic parser for simple list of dicts."""
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    key = item.get(key_field) or item.get("character_id") or item.get("weapon_id")
                    if key:
                        target_dict[f"{patch_ns}_{str(key).lower()}"] = item
        elif isinstance(items, dict):
            for k, v in items.items():
                if isinstance(v, dict):
                    target_dict[f"{patch_ns}_{str(k).lower()}"] = v
