import math

class TTKCalculator:
    def __init__(self, target_hp=200, target_vest_lvl=3, target_helmet_lvl=2):
        self.target_hp = target_hp
        self.target_vest_lvl = target_vest_lvl
        self.target_helmet_lvl = target_helmet_lvl

    def calculate_effective_damage(self, base_damage, armor_pen, damage_boost=0.0):
        """
        Calculates body shot damage factoring armor reduction & penetration
        """
        # Armor reduction values per level (Level 0 to 4)
        vest_reductions = {0: 0.0, 1: 0.33, 2: 0.45, 3: 0.50, 4: 0.55}
        base_reduction = vest_reductions.get(self.target_vest_lvl, 0.0)

        # Apply armor penetration mitigation
        effective_reduction = max(0.0, base_reduction - armor_pen)
        
        # Calculate raw damage after passive skills/boosts
        boosted_damage = base_damage * (1.0 + damage_boost)
        
        # Calculate final effective damage applied to HP
        effective_damage = boosted_damage * (1.0 - effective_reduction)
        return max(1.0, round(effective_damage, 2))  # Floor at 1.0 to prevent DivByZero

    def calculate_weapon_ttk(self, weapon_stats, player_boosts=None):
        """
        Calculates Effective Damage, BTK, and TTK
        """
        if player_boosts is None:
            player_boosts = {}

        # Safe extraction with fallback values
        base_damage = weapon_stats.get("base_damage", weapon_stats.get("damage", 0))
        rate_of_fire = weapon_stats.get("rate_of_fire", weapon_stats.get("fire_rate", 1.0))
        armor_pen = weapon_stats.get("armor_penetration", 0.0)
        damage_boost = player_boosts.get("damage_boost", 0.0)

        # Fallback safeguard if damage missing
        if base_damage <= 0:
            return {
                "effective_damage": 0.0,
                "btk": float('inf'),
                "ttk": float('inf')
            }

        eff_dmg = self.calculate_effective_damage(base_damage, armor_pen, damage_boost)
        
        # Bullets To Kill (BTK)
        btk = math.ceil(self.target_hp / eff_dmg)

        # Time To Kill (TTK) in seconds
        # Shots firing interval = 1 / rate_of_fire
        ttk = round((btk - 1) / rate_of_fire, 3)

        return {
            "effective_damage": eff_dmg,
            "btk": btk,
            "ttk": ttk
        }
