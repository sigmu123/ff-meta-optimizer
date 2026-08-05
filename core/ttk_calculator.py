import math

class MechanicsEngine:
    @staticmethod
    def calculate_effective_damage(base_dmg, range_decay_pct, vest_absorb_pct, armor_pen_pct):
        """
        Calculates exact effective damage after applying range drop and armor penetration logic.
        """
        dmg_after_range = base_dmg * (1.0 - range_decay_pct)
        effective_absorb = vest_absorb_pct * (1.0 - armor_pen_pct)
        effective_damage = dmg_after_range * (1.0 - effective_absorb)
        return round(effective_damage, 2)

    @staticmethod
    def calculate_ttk(target_hp, effective_dmg, rate_of_fire_sec):
        """
        Calculates Bullets To Kill (BTK) and exact Time To Kill (TTK) in seconds.
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
    def calculate_weapon_ttk(cls, weapon_data, target_hp=200, vest_absorb_pct=0.0, armor_pen_pct=0.0, range_decay_pct=0.0):
        """
        Helper method to compute TTK directly from JSON weapon attributes.
        """
        base_dmg = weapon_data.get("base_damage", 0)
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
    # Test G36 Assault mode TTK baseline
    sample_g36 = {
        "weapon_id": "g36_assault",
        "base_damage": 26,
        "rate_of_fire_seconds": 0.096
    }
    result = MechanicsEngine.calculate_weapon_ttk(sample_g36, target_hp=200)
    print(f"[TTK TEST G36]: Effective Damage = {result['effective_damage']} | BTK = {result['btk']} | TTK = {result['ttk_sec']}s")
