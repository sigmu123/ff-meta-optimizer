import math
from typing import Dict, Any

class MechanicsEngine:
    @staticmethod
    def calculate_effective_damage(
        base_dmg: float,
        range_decay_pct: float,
        vest_absorb_pct: float,
        armor_pen_pct: float
    ) -> float:
        """
        Micro-Variable Damage Equation:
        Effective Dmg = Base Dmg * (1 - Range Decay %) * [1 - Vest Absorption % * (1 - Armor Pen %)]
        """
        dmg_after_range = base_dmg * (1.0 - range_decay_pct)
        effective_vest_absorption = vest_absorb_pct * (1.0 - armor_pen_pct)
        effective_damage = dmg_after_range * (1.0 - effective_vest_absorption)
        return round(effective_damage, 2)

    @staticmethod
    def calculate_ttk(target_hp: float, effective_dmg: float, rate_of_fire_sec: float) -> Dict[str, Any]:
        """
        Calculates Bullets To Kill (BTK) and exact Time To Kill (TTK) in seconds.
        BTK = Ceil(Target HP / Effective Dmg)
        TTK = (BTK - 1) * Rate of Fire (sec)
        """
        if effective_dmg <= 0:
            return {"btk": float('inf'), "ttk_sec": float('inf')}
        
        btk = math.ceil(target_hp / effective_dmg)
        ttk_sec = round((btk - 1) * rate_of_fire_sec, 3)
        
        return {
            "btk": btk,
            "ttk_sec": ttk_sec
        }

    @classmethod
    def calculate_weapon_ttk(
        cls,
        weapon_data: Dict[str, Any],
        target_hp: float = 200.0,
        vest_absorb_pct: float = 0.0,
        armor_pen_pct: float = 0.0,
        range_decay_pct: float = 0.0
    ) -> Dict[str, Any]:
        """
        Helper method to compute TTK directly from JSON weapon attributes.
        """
        base_dmg = weapon_data.get("base_damage", 0.0)
        rof = weapon_data.get("rate_of_fire_seconds", 0.1)
        
        eff_dmg = cls.calculate_effective_damage(base_dmg, range_decay_pct, vest_absorb_pct, armor_pen_pct)
        ttk_info = cls.calculate_ttk(target_hp, eff_dmg, rof)
        
        return {
            "weapon_id": weapon_data.get("weapon_id", "unknown"),
            "effective_damage": eff_dmg,
            "btk": ttk_info["btk"],
            "ttk_sec": ttk_info["ttk_sec"]
        }


if __name__ == "__main__":
    sample_weapon = {
        "weapon_id": "g36_assault",
        "base_damage": 26,
        "rate_of_fire_seconds": 0.096
    }
    res = MechanicsEngine.calculate_weapon_ttk(
        sample_weapon,
        target_hp=200,
        vest_absorb_pct=0.33,
        armor_pen_pct=0.10,
        range_decay_pct=0.05
    )
    print(f"[ENGINE UNIT TEST] Effective Damage: {res['effective_damage']} | BTK: {res['btk']} | TTK: {res['ttk_sec']}s")
