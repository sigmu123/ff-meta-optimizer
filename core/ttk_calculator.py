import math
import re

class TTKCalculator:
    def __init__(self, target_hp=200, target_vest_lvl=3, target_helmet_lvl=2, engagement_distance=15):
        self.target_hp = target_hp
        self.target_vest_lvl = target_vest_lvl
        self.target_helmet_lvl = target_helmet_lvl
        self.engagement_distance = engagement_distance

    def calculate_effective_damage(self, base_damage, armor_pen=0.0, damage_boost=0.0, distance_decay=0.0, hit_type="body"):
        vest_reductions = {0: 0.0, 1: 0.33, 2: 0.45, 3: 0.50, 4: 0.55}
        helmet_reductions = {0: 0.0, 1: 0.33, 2: 0.45, 3: 0.57, 4: 0.60}
        
        if hit_type == "head":
            base_reduction = helmet_reductions.get(self.target_helmet_lvl, 0.0)
            base_damage *= 5.5
        else:
            base_reduction = vest_reductions.get(self.target_vest_lvl, 0.0)

        effective_reduction = max(0.0, base_reduction - armor_pen)
        
        decayed_base = base_damage * (1.0 - distance_decay)
        boosted_damage = decayed_base * (1.0 + damage_boost)
        
        effective_damage = boosted_damage * (1.0 - effective_reduction)
        return max(1.0, round(effective_damage, 2))

    def _parse_float_advanced(self, val):
        if isinstance(val, (int, float)):
            return float(val), False
        if isinstance(val, str):
            try:
                is_pct = "%" in val
                cleaned = re.sub(r'[^\d.-]', '', val)
                if "-" in cleaned and len(cleaned) > 1:
                    parts = cleaned.split("-")
                    cleaned = parts[0] if parts[0] else parts[1]
                return float(cleaned) if cleaned else 0.0, is_pct
            except ValueError:
                return 0.0, False
        return 0.0, False

    def calculate_weapon_ttk(self, weapon_stats, player_boosts=None):
        if player_boosts is None: 
            player_boosts = {}
        if not isinstance(weapon_stats, dict):
            return {"effective_damage": 0.0, "btk": float('inf'), "ttk": float('inf')}

        raw_damage = weapon_stats.get("base_damage") or weapon_stats.get("damage") or 28.0
        parsed_dmg, dmg_is_pct = self._parse_float_advanced(raw_damage)
        base_damage = 28.0 * (1.0 + (parsed_dmg / 100.0)) if dmg_is_pct else (parsed_dmg if parsed_dmg > 0 else 28.0)

        raw_rof = weapon_stats.get("rate_of_fire") or weapon_stats.get("fire_rate") or 0.20
        parsed_rof, rof_is_pct = self._parse_float_advanced(raw_rof)
        rate_of_fire = 0.20 * (1.0 - (parsed_rof / 100.0)) if rof_is_pct else (parsed_rof if parsed_rof > 0 else 0.20)

        raw_ap = weapon_stats.get("armor_penetration") or weapon_stats.get("armor_pen") or 0.0
        parsed_ap, ap_is_pct = self._parse_float_advanced(raw_ap)
        armor_pen = parsed_ap / 100.0 if parsed_ap > 1.0 or ap_is_pct else parsed_ap
        
        range_stat, _ = self._parse_float_advanced(weapon_stats.get("range", 0.0))
        dist_decay = min(0.6, (self.engagement_distance / max(1, range_stat)) * 0.1) if range_stat > 0 else 0.0

        if base_damage <= 0 or rate_of_fire <= 0:
            return {"effective_damage": 0.0, "btk": float('inf'), "ttk": float('inf')}

        eff_dmg = self.calculate_effective_damage(base_damage, armor_pen, player_boosts.get("damage_boost", 0.0), dist_decay)
        btk = math.ceil(self.target_hp / eff_dmg)
        
        ttk = round((btk - 1) * rate_of_fire, 3)
        return {"effective_damage": eff_dmg, "btk": btk, "ttk": ttk, "rate_of_fire": rate_of_fire}

MechanicsEngine = TTKCalculator
