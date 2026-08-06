import math
import json
import os
from typing import Dict, Any, Optional

class RampageDamageEngine:
    """
    Quantitative Game Engine Math for Free Fire Rampage Patch.
    Integrates dynamic character multipliers, armor penetration, safezone scaling,
    and weapon attributes directly from versioned JSON files.
    """
    
    def __init__(self, patch_path: str = "data/patches/patch_rampage"):
        self.patch_path = patch_path
        self.active_skills = self._load_json(f"{patch_path}/characters/active_skills.json")
        self.passive_skills = self._load_json(f"{patch_path}/characters/passive_skills.json")
        self.weapons = self._load_json(f"{patch_path}/weapons/base_attributes.json")
        self.mechanics = self._load_json(f"{patch_path}/mechanics/gameplay_rules.json")

    def _load_json(self, file_path: str) -> Dict[str, Any]:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return {}

    def get_wolfrahh_headshot_bonus(self, spectators: int, skill_level: int = 6) -> float:
        """
        Calculates Wolfrahh Limelight headshot bonus based on spectator count.
        Max 30% bonus at level 6.
        """
        level_idx = min(max(skill_level - 1, 0), 5)
        spec_rates = [0.02, 0.03, 0.04, 0.06, 0.08, 0.10]
        max_caps = [0.20, 0.22, 0.24, 0.26, 0.28, 0.30]
        
        bonus = spectators * spec_rates[level_idx]
        return min(bonus, max_caps[level_idx])

    def get_misha_damage_reduction(self, skill_level: int = 6) -> float:
        """
        Returns Misha Afterburner incoming damage mitigation percentage.
        """
        level_idx = min(max(skill_level - 1, 0), 5)
        reductions = [0.05, 0.06, 0.08, 0.11, 0.15, 0.28]
        return reductions[level_idx]

    def calculate_effective_damage(
        self,
        base_damage: float,
        range_decay_pct: float,
        vest_absorption_pct: float,
        armor_pen_pct: float,
        is_headshot: bool = False,
        headshot_multiplier: float = 2.0,
        attacker_wolfrahh_specs: int = 0,
        defender_in_misha_vehicle: bool = False,
        steffie_aura_active: bool = False,
        steffie_level: int = 6
    ) -> float:
        """
        Full Micro-Variable Damage Equation.
        Effective Dmg = Base Dmg * (1 - Range Decay %) * [1 - Vest Absorption % * (1 - Armor Pen %)]
        """
        # Range decay calculation
        effective_dmg = base_damage * (1.0 - range_decay_pct)

        # Headshot & Wolfrahh Modifier
        if is_headshot:
            wolf_bonus = self.get_wolfrahh_headshot_bonus(attacker_wolfrahh_specs)
            effective_dmg *= (headshot_multiplier + wolf_bonus)

        # Armor Absorption Equation
        effective_vest_abs = vest_absorption_pct * (1.0 - armor_pen_pct)
        effective_dmg *= (1.0 - effective_vest_abs)

        # Steffie Painted Refuge Reduction
        if steffie_aura_active:
            steffie_red = [0.10, 0.12, 0.14, 0.16, 0.18, 0.20][min(max(steffie_level - 1, 0), 5)]
            effective_dmg *= (1.0 - steffie_red)

        # Misha Vehicle Defensive Mitigation
        if defender_in_misha_vehicle:
            misha_red = self.get_misha_damage_reduction()
            effective_dmg *= (1.0 - misha_red)

        return max(effective_dmg, 0.0)

    def calculate_ttk(self, effective_damage: float, target_hp: float, rate_of_fire_ms: float) -> Dict[str, Any]:
        """
        Calculates Bullets To Kill (BTK) and Time To Kill (TTK in seconds).
        """
        if effective_damage <= 0:
            return {"btk": math.inf, "ttk_sec": math.inf}
            
        btk = math.ceil(target_hp / effective_damage)
        ttk_sec = (btk - 1) * (rate_of_fire_ms / 1000.0)
        
        return {
            "btk": btk,
            "ttk_sec": round(ttk_sec, 3)
        }
