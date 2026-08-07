import math

class TTKCalculator:
    def __init__(self, target_hp=200, target_vest_lvl=3, target_helmet_lvl=2):
        self.target_hp = target_hp
        self.target_vest_lvl = target_vest_lvl
        self.target_helmet_lvl = target_helmet_lvl

    def calculate_effective_damage(self, base_damage, armor_pen=0.0, damage_boost=0.0):
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
        Calculates Effective Damage, BTK, and TTK with robust JSON key extraction
        """
        if player_boosts is None:
            player_boosts = {}

        if isinstance(weapon_stats, list):
            # Fallback if list passed instead of dict
            return {"effective_damage": 0.0, "btk": float('inf'), "ttk": float('inf')}

        # Safe extraction for damage keys across different JSON patches
        base_damage = (
            weapon_stats.get("base_damage") or 
            weapon_stats.get("damage") or 
            weapon_stats.get("base_dmg") or 
            0.0
        )
        
        # Safe extraction for rate of fire keys
        rate_of_fire = (
            weapon_stats.get("rate_of_fire") or 
            weapon_stats.get("fire_rate") or 
            weapon_stats.get("rof") or 
            1.0
        )

        armor_pen = weapon_stats.get("armor_penetration", weapon_stats.get("armor_pen", 0.0))
        damage_boost = player_boosts.get("damage_boost", 0.0)

        # Fallback safeguard if base damage is missing or zero
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
        ttk = round((btk - 1) / rate_of_fire, 3) if rate_of_fire > 0 else float('inf')

        return {
            "effective_damage": eff_dmg,
            "btk": btk,
            "ttk": ttk
        }

    # Alias method to support legacy calls in combinatorial_tester.py
    def process_weapon_mechanics(self, weapon_stats, player_boosts=None):
        return self.calculate_weapon_ttk(weapon_stats, player_boosts)


# Export Class Aliases to resolve ImportError in legacy imports
MechanicsEngine = TTKCalculator
