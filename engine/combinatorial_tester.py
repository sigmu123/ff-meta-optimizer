import time
from typing import Dict, List, Any

class CombinatorialOptimizer:
    def __init__(self, mode: str = "CS"):
        self.mode = mode.upper()

    def run_global_cross_patch_sweep(self, all_patches_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merges ALL patch eras into a single unified matrix pool and evaluates
        hyper-combinations across the entire chronological timeline.
        """
        start_time = time.perf_counter()

        merged_actives = {}
        merged_passives = {}
        merged_weapons = {}
        merged_pets = {}
        merged_loadouts = {}

        # 1. Aggregate and Merge Data Across All Patches
        for patch_name, patch_content in all_patches_data.items():
            # Extract Characters
            chars = patch_content.get("characters", [])
            for c in chars:
                if isinstance(c, dict):
                    c_id = str(c.get("character_id", c.get("character_name", c.get("name", "")))).lower()
                    if c_id:
                        if c.get("type") == "Active" or "active" in c_id or c.get("cooldown_seconds") or c.get("skill_boosts"):
                            merged_actives[c_id] = c
                        else:
                            merged_passives[c_id] = c

            # Extract Weapons
            weaps = patch_content.get("weapons", [])
            for w in weaps:
                if isinstance(w, dict):
                    w_id = str(w.get("weapon_id", w.get("weapon_name", w.get("name", "")))).lower()
                    if w_id:
                        merged_weapons[w_id] = w

            # Extract Pets & Loadouts
            pets_loadout = patch_content.get("pets_loadout", {})
            for key, val in pets_loadout.items():
                if "pets" in key and isinstance(val, dict):
                    p_list = val.get("pets", [])
                    for p in p_list:
                        if isinstance(p, dict):
                            merged_pets[str(p.get("pet_id", p.get("pet_name", ""))).lower()] = p
                elif "loadouts" in key and isinstance(val, dict):
                    l_list = val.get("loadouts", [])
                    for l in l_list:
                        if isinstance(l, dict):
                            merged_loadouts[str(l.get("loadout_id", l.get("loadout_name", ""))).lower()] = l

        # Fallbacks for baseline items if missing from JSON schema
        if not merged_actives:
            merged_actives = {"chrono": {"name": "Chrono"}, "kenta": {"name": "Kenta"}, "alok": {"name": "Alok"}, "wukong": {"name": "Wukong"}, "a124": {"name": "A124"}}
        if not merged_weapons:
            merged_weapons = {"mp40": {"name": "MP40"}, "m1887": {"name": "M1887"}, "m82b": {"name": "M82B"}, "g36_assault": {"name": "G36"}, "parafal": {"name": "PARAFAL"}}
        if not merged_pets:
            merged_pets = {"rockie": {"name": "Rockie"}, "beaston": {"name": "Beaston"}, "dreki": {"name": "Dreki"}}
        if not merged_loadouts:
            merged_loadouts = {"armor_crate": {"name": "Armor Crate"}, "secret_clue": {"name": "Secret Clue"}, "bonfire": {"name": "Bonfire"}}

        active_keys = list(merged_actives.keys())
        weapon_keys = list(merged_weapons.keys())
        pet_keys = list(merged_pets.keys())
        loadout_keys = list(merged_loadouts.keys())

        best_score = -1.0
        best_combo = {}
        total_tested = 0

        w_dmg = 0.40 if self.mode == "CS" else 0.25
        w_rof = 0.30 if self.mode == "CS" else 0.25
        w_mob = 0.20 if self.mode == "CS" else 0.25
        w_util = 0.10 if self.mode == "CS" else 0.25

        # 2. Universal Matrix Cross-Sweep Loop
        for active in active_keys:
            for pet in pet_keys:
                for loadout in loadout_keys:
                    for weap in weapon_keys:
                        total_tested += 1

                        # Dynamic attribute-based scoring
                        w_data = merged_weapons.get(weap, {})
                        dmg_val = float(w_data.get("base_damage", 80 if "m82b" in weap or "m1887" in weap else 25))
                        status = str(w_data.get("status", "")).lower()
                        rarity = str(w_data.get("rarity_tier", "")).lower()

                        dmg_score = 95.0 if (status == "buffed" or rarity == "gold" or dmg_val > 50) else 75.0
                        rof_score = 90.0 if "mp40" in weap or "mac10" in weap else 70.0
                        mob_score = 92.0 if "chrono" in active or "oscar" in active or "alok" in active else 70.0
                        util_score = 90.0 if "rockie" in pet else 75.0

                        combo_score = (dmg_score * w_dmg) + (rof_score * w_rof) + (mob_score * w_mob) + (util_score * w_util)

                        if combo_score > best_score:
                            best_score = combo_score
                            best_combo = {
                                "active_skill": active,
                                "primary_weapon": weap,
                                "pet": pet,
                                "loadout": loadout,
                                "mode": self.mode,
                                "meta_score": round(combo_score, 2)
                            }

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 3)

        return {
            "execution_time_ms": execution_time_ms,
            "total_permutations": total_tested,
            "merged_entities_count": {
                "active_skills": len(active_keys),
                "weapons": len(weapon_keys),
                "pets": len(pet_keys),
                "loadouts": len(loadout_keys)
            },
            "best_combination": best_combo
        }
