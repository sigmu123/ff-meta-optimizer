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
    def calculate_ttk(target_hp, effective_dmg, rate_of_fire_ms):
        """
        Calculates Bullets To Kill (BTK) and exact Time To Kill (TTK) in seconds.
        """
        if effective_dmg <= 0:
            return {"btk": float('inf'), "ttk_sec": float('inf')}
        
        btk = math.ceil(target_hp / effective_dmg)
        ttk_sec = round(((btk - 1) * rate_of_fire_ms) / 1000.0, 3)
        
        return {
            "btk": btk,
            "ttk_sec": ttk_sec
        }
