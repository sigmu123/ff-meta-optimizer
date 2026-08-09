import os
import sys
import random
import itertools
from core.ttk_calculator import TTKCalculator
from patch_loader import PatchLoader
from interface.prompt_parser import parse_full_prompt

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class HybridMetaEngine:
    def __init__(self, patch_name="patch_ob54", objective="max_damage", playstyle="rush", engagement_range="mid"):
        self.patch_name = patch_name
        self.loader = PatchLoader(patch_name=patch_name, base_dir=current_dir)
        self.ttk_calc = TTKCalculator()

        # Build data from patches (dynamic)
        self._build_data_from_patches()
        # Apply additional adjustments (if any)
        self._apply_patch_adjustments()

        self.objective = objective
        self.playstyle = playstyle
        self.engagement_range = engagement_range
        # Set TTK calculator engagement distance based on range
        if engagement_range == "close":
            self.ttk_calc.engagement_distance = 10
        elif engagement_range == "long":
            self.ttk_calc.engagement_distance = 50
        else:  # mid
            self.ttk_calc.engagement_distance = 25

    def _build_data_from_patches(self):
        """Load weapons and character skills directly from patch loader."""
        # Characters
        self.actives = {}
        self.passives = {}
        # Merge loader's active and passive skills into dictionaries
        for key, val in self.loader.active_skills.items():
            # key format: patch_ns_charactername
            char_name = key.split('_', 1)[-1] if '_' in key else key
            self.actives[char_name] = val
        for key, val in self.loader.passive_skills.items():
            char_name = key.split('_', 1)[-1] if '_' in key else key
            self.passives[char_name] = val

        # If no skills loaded, fallback to base
        if not self.actives:
            self.actives = {
                "alok": {"skill_name": "Drop the Beat", "type": "active", "cooldown": 45, "duration": 10, "heal": 5, "speed_boost": 15},
                "chrono": {"skill_name": "Time Turner", "type": "active", "cooldown": 60, "duration": 6, "shield_hp": 800},
                "k": {"skill_name": "Master of All", "type": "active", "cooldown": 3, "duration": 0, "ep_recovery": 3},
                "orion": {"skill_name": "Crimson Crush", "type": "active", "cooldown": 3, "duration": 3, "damage": 15},
                "tatsuya": {"skill_name": "Rebel Rush", "type": "active", "cooldown": 98, "duration": 0.3, "charges": 2},
                "steffie": {"skill_name": "Painted Refuge", "type": "active", "cooldown": 45, "duration": 10, "bullet_damage_reduction": 5, "explosive_damage_reduction": 15},
                "kenta": {"skill_name": "Swordsman's Wrath", "type": "active", "cooldown": 70, "duration": 5, "frontal_damage_reduction": 60},
                "dimitri": {"skill_name": "Healing Heartbeat", "type": "active", "cooldown": 60, "duration": 12, "heal": 10},
            }
        if not self.passives:
            self.passives = {
                "kelly": {"skill_name": "Dash", "type": "passive", "speed_boost": 6},
                "hayato": {"skill_name": "Art of Blades", "type": "passive", "armor_pen": 5},
                "moco": {"skill_name": "Hacker's Eye", "type": "passive", "mark_duration": 4},
                "jota": {"skill_name": "Sustained Raids", "type": "passive", "hp_on_hit": 5},
                "andrew": {"skill_name": "Armor Specialist", "type": "passive", "armor_reduction": 25},
                "antonio": {"skill_name": "Gangster's Spirit", "type": "passive", "extra_hp": 35},
                "kapella": {"skill_name": "Healing Song", "type": "passive", "heal_increase": 20, "revive_shield": 80},
                "olivia": {"skill_name": "Healing Touch", "type": "passive", "heal_spread": 80},
                "maxim": {"skill_name": "Gluttony", "type": "passive", "heal_increase": 25},
            }

        # Weapons: load from loader's weapons dict
        self.weapons = {}
        for key, stats in self.loader.weapons.items():
            # key format: patch_ns_weaponname
            wep_name = key.split('_', 1)[-1] if '_' in key else key
            # Ensure required fields
            if "damage" not in stats:
                stats["damage"] = 28.0
            if "rate_of_fire" not in stats:
                stats["rate_of_fire"] = 0.2
            if "armor_penetration" not in stats:
                stats["armor_penetration"] = 0.0
            if "range" not in stats:
                stats["range"] = 30
            self.weapons[wep_name] = stats

        # If no weapons loaded, fallback to base
        if not self.weapons:
            self.weapons = {
                "mp40": {"damage": 30, "rate_of_fire": 0.08, "armor_penetration": 0.0, "range": 30},
                "groza": {"damage": 38, "rate_of_fire": 0.12, "armor_penetration": 0.0, "range": 40},
                "parafal": {"damage": 48, "rate_of_fire": 0.245, "armor_penetration": 0.0, "range": 50},
                "m590": {"damage": 40, "rate_of_fire": 0.2, "armor_penetration": 0.0, "range": 20},
                "m82b": {"damage": 150, "rate_of_fire": 0.4, "armor_penetration": 30, "range": 90},
                "mp48": {"damage": 28, "rate_of_fire": 0.07, "armor_penetration": 10, "range": 25},
                "famas": {"damage": 30, "rate_of_fire": 0.1, "armor_penetration": 0.0, "range": 35},
                "ak47": {"damage": 38, "rate_of_fire": 0.11, "armor_penetration": 0.0, "range": 45},
            }

        # Pets and Loadouts from loader
        self.pets = list(self.loader.pets) if self.loader.pets else ["Rockie", "Mr. Waggor", "Falco", "Ottero", "Dr. Beanie"]
        self.loadouts = list(self.loader.loadouts) if self.loader.loadouts else ["Bonfire", "Leg Pockets", "Bounty Token", "Secret Clue", "Armor Crate"]

    def _apply_patch_adjustments(self):
        # This now applies additional adjustments if any (but we already loaded stats)
        # We can still apply character/weapon adjustments from loader if needed
        # But since we loaded directly, we may skip this or just keep for compatibility
        pass

    # The rest of the methods remain similar, but we need to adjust _get_optimal_weapons
    # to consider sniper playstyle and sort by effective damage instead of DPS.

    def _get_optimal_weapons(self, squad_context=None):
        w_scores = []
        for w_id, w_data in self.weapons.items():
            if not isinstance(w_data, dict):
                continue
            # Calculate TTK and effective damage
            stats = self.ttk_calc.calculate_weapon_ttk(w_data)
            if stats and stats["ttk"] < float('inf'):
                clean_name = str(w_id).split("_")[-1].upper()
                # For sniper, use effective damage as primary score
                if self.playstyle == "sniper" and self.engagement_range == "long":
                    score = stats["effective_damage"]
                else:
                    # DPS for other playstyles
                    dps = stats["effective_damage"] * (1.0 / max(0.01, stats.get("rate_of_fire", 0.2)))
                    score = dps
                w_scores.append({"name": clean_name, "ttk": stats["ttk"], "score": score, "effective_damage": stats["effective_damage"]})
        w_scores.sort(key=lambda x: x["score"], reverse=True)
        if len(w_scores) >= 2:
            return {"primary": w_scores[0], "secondary": w_scores[1]}
        else:
            return {"primary": w_scores[0] if w_scores else {"name": "MP40", "ttk": 0.28},
                    "secondary": w_scores[0] if w_scores else {"name": "GROZA", "ttk": 0.32}}

    # Other methods like _fitness_function, run_exhaustive_search, etc. remain similar
    # but they use self.weapons which is now dynamic.

    # Note: The rest of the class (fitness, GA, exhaustive search) should be unchanged
    # except they now use the dynamic self.weapons. We'll keep them as is.

    # For completeness, include the remaining methods from original main.py,
    # but replace _build_base_data with _build_data_from_patches and adjust references.

    # I'll paste the full class with all methods in the final answer.
