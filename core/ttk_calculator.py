import math

class TTKCalculator:
    def __init__(self, target_hp=200, target_vest_lvl=3, target_helmet_lvl=2):
        self.target_hp = target_hp
        self.target_vest_lvl = target_vest_lvl
        self.target_helmet_lvl = target_helmet_lvl

    def calculate_effective_damage(self, base_damage, armor_pen=0.0, damage_boost=0.0):
        vest_reductions = {0: 0.0, 1: 0.33, 2: 0.45, 3: 0.50, 4: 0.55}
        base_reduction = vest_reductions.get(self.target_vest_lvl, 0.0)

        effective_reduction = max(0.0, base_reduction - armor_pen)
        boosted_damage = base_damage * (1.0 + damage_boost)
        effective_damage = boosted_damage * (1.0 - effective_reduction)
        
        return max(1.0, round(effective_damage, 2))

    def calculate_weapon_ttk(self, weapon_stats, player_boosts=None):
        if player_boosts is None:
            player_boosts = {}

        if not isinstance(weapon_stats, dict):
            return {"effective_damage": 0.0, "btk": float('inf'), "ttk": float('inf')}

        # Added standardized baselines so ttk != inf if schema only contains buffs
        base_damage = self._parse_float(weapon_stats.get("base_damage") or weapon_stats.get("damage") or 28.0)
        rate_of_fire = self._parse_float(weapon_stats.get("rate_of_fire") or weapon_stats.get("fire_rate") or 0.20)
        armor_pen = self._parse_float(weapon_stats.get("armor_penetration") or weapon_stats.get("armor_pen") or 0.0)
        
        if armor_pen > 1.0: 
            armor_pen = armor_pen / 100.0

        damage_boost = player_boosts.get("damage_boost", 0.0)

        if base_damage <= 0:
            return {"effective_damage": 0.0, "btk": float('inf'), "ttk": float('inf')}

        eff_dmg = self.calculate_effective_damage(base_damage, armor_pen, damage_boost)
        btk = math.ceil(self.target_hp / eff_dmg)
        
        ttk = round((btk - 1) * rate_of_fire, 3) if rate_of_fire > 0 else float('inf')

        return {
            "effective_damage": eff_dmg,
            "btk": btk,
            "ttk": ttk
        }

    def _parse_float(self, val):
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            try:
                return float(val.replace("%", "").replace("+", "").strip())
            except ValueError:
                return 0.0
        return 0.0

MechanicsEngine = TTKCalculator
