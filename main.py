import os
import sys
import random
from core.ttk_calculator import TTKCalculator
from patch_loader import PatchLoader

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class HybridMetaEngine:
    def __init__(self, patch_name="patch_ob54"):
        self.patch_name = patch_name
        self.loader = PatchLoader(patch_name=patch_name, base_dir=current_dir)
        self.ttk_calc = TTKCalculator()

        # Build base datasets (fallback defaults if loader yields nothing)
        self._build_base_data()

        # Apply patch adjustments to base data
        self._apply_patch_adjustments()

    def _build_base_data(self):
        """Define default characters, weapons, pets, loadouts."""
        # Default active skills (name: base stats)
        self.base_actives = {
            "alok": {"skill_name": "Drop the Beat", "type": "active", "cooldown": 45, "duration": 10, "heal": 5, "speed_boost": 15},
            "chrono": {"skill_name": "Time Turner", "type": "active", "cooldown": 60, "duration": 6, "shield_hp": 800},
            "k": {"skill_name": "Master of All", "type": "active", "cooldown": 3, "duration": 0, "ep_recovery": 3},
            "orion": {"skill_name": "Crimson Crush", "type": "active", "cooldown": 3, "duration": 3, "damage": 15},
            "tatsuya": {"skill_name": "Rebel Rush", "type": "active", "cooldown": 98, "duration": 0.3, "charges": 2},
        }
        self.base_passives = {
            "kelly": {"skill_name": "Dash", "type": "passive", "speed_boost": 6},
            "hayato": {"skill_name": "Art of Blades", "type": "passive", "armor_pen": 5},
            "moco": {"skill_name": "Hacker's Eye", "type": "passive", "mark_duration": 4},
            "jota": {"skill_name": "Sustained Raids", "type": "passive", "hp_on_hit": 5},
            "andrew": {"skill_name": "Armor Specialist", "type": "passive", "armor_reduction": 25},
        }
        self.base_weapons = {
            "mp40": {"damage": 30, "rate_of_fire": 0.08, "armor_pen": 0.0, "range": 30},
            "groza": {"damage": 38, "rate_of_fire": 0.12, "armor_pen": 0.0, "range": 40},
            "parafal": {"damage": 48, "rate_of_fire": 0.245, "armor_pen": 0.0, "range": 50},
            "m590": {"damage": 40, "rate_of_fire": 0.2, "armor_pen": 0.0, "range": 20},
            "m82b": {"damage": 150, "rate_of_fire": 0.4, "armor_pen": 30, "range": 90},
            "mp48": {"damage": 28, "rate_of_fire": 0.07, "armor_pen": 10, "range": 25},
            "famas": {"damage": 30, "rate_of_fire": 0.1, "armor_pen": 0.0, "range": 35},
            "ak47": {"damage": 38, "rate_of_fire": 0.11, "armor_pen": 0.0, "range": 45},
        }
        self.base_pets = ["Rockie", "Mr. Waggor", "Falco", "Ottero", "Dr. Beanie"]
        self.base_loadouts = ["Bonfire", "Leg Pockets", "Bounty Token", "Secret Clue", "Armor Crate"]

        # Initialize working copies
        self.actives = dict(self.base_actives)
        self.passives = dict(self.base_passives)
        self.weapons = dict(self.base_weapons)
        self.pets = list(self.base_pets)
        self.loadouts = list(self.base_loadouts)

    def _apply_patch_adjustments(self):
        """Override base stats with patch adjustments (if any)."""
        # ---- Characters ----
        for char_name, adjustments in self.loader.character_adjustments.items():
            # Find matching base entry (active or passive)
            for adj in adjustments:
                skill_name = adj.get("skill_name") or ""
                # Determine if active or passive
                is_active = False
                if "active" in str(adj.get("type", "")).lower():
                    is_active = True
                elif "passive" in str(adj.get("type", "")).lower():
                    is_active = False
                else:
                    # heuristic
                    if "cooldown" in adj or "duration" in adj:
                        is_active = True

                if is_active:
                    if char_name.lower() in self.actives:
                        self._apply_character_adjustment(self.actives[char_name.lower()], adj)
                    else:
                        # Add new active skill
                        new_skill = {"skill_name": skill_name, "type": "active"}
                        self._apply_character_adjustment(new_skill, adj)
                        self.actives[char_name.lower()] = new_skill
                else:
                    if char_name.lower() in self.passives:
                        self._apply_character_adjustment(self.passives[char_name.lower()], adj)
                    else:
                        new_skill = {"skill_name": skill_name, "type": "passive"}
                        self._apply_character_adjustment(new_skill, adj)
                        self.passives[char_name.lower()] = new_skill

        # ---- Weapons ----
        for wep_name, adjustments in self.loader.weapon_adjustments.items():
            if wep_name.lower() in self.weapons:
                for adj in adjustments:
                    self._apply_weapon_adjustment(self.weapons[wep_name.lower()], adj)
            else:
                # Add new weapon with base stats from adjustment (if any)
                new_wep = {}
                for adj in adjustments:
                    self._apply_weapon_adjustment(new_wep, adj)
                if new_wep:
                    self.weapons[wep_name.lower()] = new_wep

        # ---- Pets & Loadouts (merge from loader) ----
        if self.loader.pets:
            for pet in self.loader.pets:
                if pet not in self.pets:
                    self.pets.append(pet)
        if self.loader.loadouts:
            for ld in self.loader.loadouts:
                if ld not in self.loadouts:
                    self.loadouts.append(ld)

    def _apply_character_adjustment(self, skill, adj):
        """Apply numeric adjustments to a skill dict."""
        # Map adjustment keys to skill keys
        mapping = {
            "cooldown_seconds": "cooldown",
            "duration_seconds": "duration",
            "shield_hp": "shield_hp",
            "damage": "damage",
            "heal": "heal",
            "hp_recovery_per_second": "heal",
            "movement_speed_boost_percent": "speed_boost",
            "armor_penetration": "armor_pen",
        }
        for adj_key, skill_key in mapping.items():
            if adj_key in adj:
                skill[skill_key] = adj[adj_key]
        # Also handle "old_value"/"new_value" patterns if needed
        if "new_value" in adj:
            for k, v in adj.items():
                if k not in ["character_name", "skill_name", "type", "adjustment_type"]:
                    if isinstance(v, dict) and "new_value" in v:
                        skill[k] = v["new_value"]

    def _apply_weapon_adjustment(self, weapon, adj):
        """Apply numeric adjustments to a weapon dict."""
        mapping = {
            "damage_percentage_change": "damage",
            "rate_of_fire_percentage_change": "rate_of_fire",
            "armor_penetration_percentage_change": "armor_pen",
            "range_percentage_change": "range",
            "magazine_capacity": "magazine",
        }
        for adj_key, stat_key in mapping.items():
            if adj_key in adj:
                val = adj[adj_key]
                if isinstance(val, (int, float)):
                    if stat_key in weapon:
                        # Apply percentage change
                        if "percentage" in adj_key or "%" in str(adj_key):
                            weapon[stat_key] *= (1 + val / 100.0)
                        else:
                            weapon[stat_key] += val
                    else:
                        weapon[stat_key] = val
        # Handle absolute changes
        if "base_damage_percentage_change" in adj:
            if "damage" in weapon:
                weapon["damage"] *= (1 + adj["base_damage_percentage_change"] / 100.0)
        if "armor_penetration" in adj:
            weapon["armor_pen"] = adj["armor_penetration"]

    # ---- Genetic Algorithm methods (unchanged structure) ----
    def _is_valid_chromosome(self, active, p1, p2, p3):
        passive_set = {p1, p2, p3}
        if len(passive_set) != 3:
            return False
        if active in passive_set:
            return False
        return True

    def _generate_random_valid_squad(self):
        active_list = list(self.actives.keys())
        passive_list = list(self.passives.keys())
        if len(passive_list) < 3:
            return {"active": active_list[0], "passives": (passive_list * 3)[:3], "pet": self.pets[0], "loadout": self.loadouts[0]}
        attempts = 0
        while attempts < 100:
            act = random.choice(active_list)
            p1, p2, p3 = random.sample(passive_list, 3)
            if self._is_valid_chromosome(act, p1, p2, p3):
                return {
                    "active": act,
                    "passives": sorted([p1, p2, p3]),
                    "pet": random.choice(self.pets),
                    "loadout": random.choice(self.loadouts)
                }
            attempts += 1
        return {"active": active_list[0], "passives": sorted(passive_list[:3]), "pet": self.pets[0], "loadout": self.loadouts[0]}

    def _fitness_function(self, squad):
        score = 60.0
        best_weapons = self._get_optimal_weapons(squad)
        if best_weapons["primary"]["ttk"] < 0.35:
            score += 15.0
        if best_weapons["secondary"]["ttk"] < 0.40:
            score += 10.0
        return min(99.9, score)

    def _crossover_and_mutate(self, parent1, parent2):
        child = {
            "active": parent1["active"] if random.random() > 0.5 else parent2["active"],
            "pet": parent1["pet"] if random.random() > 0.5 else parent2["pet"],
            "loadout": parent2["loadout"]
        }
        combined_passives = list(set(parent1["passives"] + parent2["passives"]))
        available_pool = [p for p in combined_passives if p != child["active"]]
        if len(available_pool) >= 3:
            child["passives"] = sorted(random.sample(available_pool, 3))
        else:
            child["passives"] = parent1["passives"]
        if random.random() < 0.1:
            child["active"] = random.choice(list(self.actives.keys()))
        if not self._is_valid_chromosome(child["active"], *child["passives"]):
            return self._generate_random_valid_squad()
        return child

    def run_ga_pipeline(self, generations=25, population_size=200, output_limit=10):
        population = [self._generate_random_valid_squad() for _ in range(population_size)]
        for gen in range(generations):
            scored_pop = [(squad, self._fitness_function(squad)) for squad in population]
            scored_pop.sort(key=lambda x: x[1], reverse=True)
            survivors = [x[0] for x in scored_pop[:max(2, population_size // 2)]]
            next_gen = survivors.copy()
            while len(next_gen) < population_size:
                p1, p2 = random.sample(survivors, 2)
                next_gen.append(self._crossover_and_mutate(p1, p2))
            population = next_gen
        final_scored = [(squad, self._fitness_function(squad)) for squad in population]
        final_scored.sort(key=lambda x: x[1], reverse=True)
        unique_squads = []
        seen_signatures = set()
        for squad, score in final_scored:
            signature = (squad["active"], tuple(squad["passives"]), squad["pet"], squad["loadout"])
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_squads.append((squad, score))
            if len(unique_squads) == output_limit:
                break
        return unique_squads

    def apply_context_multipliers(self, top_squads, playstyle="rush"):
        results = []
        for squad, base_score in top_squads:
            final_score = base_score
            if playstyle == "rush" and str(squad["loadout"]).lower() == "leg pockets":
                final_score *= 1.05
            if playstyle == "sniper":
                final_score *= 1.08
            best_weapons = self._get_optimal_weapons(squad)
            scaled_win_rate = (final_score / 120.0) * 100
            results.append({
                "build": squad,
                "win_rate": round(min(99.99, scaled_win_rate), 2),
                "weapons": best_weapons
            })
        return sorted(results, key=lambda x: x["win_rate"], reverse=True)

    def _get_optimal_weapons(self, squad_context=None):
        w_scores = []
        for w_id, w_data in self.weapons.items():
            if not isinstance(w_data, dict):
                continue
            stats = self.ttk_calc.calculate_weapon_ttk(w_data)
            if stats and "ttk" in stats and 0 < stats["ttk"] < float('inf'):
                dps = stats["effective_damage"] * (1.0 / max(0.01, stats.get("rate_of_fire", 0.2)))
                clean_name = str(w_id).split("_")[-1].upper()
                w_scores.append({"name": clean_name, "ttk": stats["ttk"], "score": dps})
        w_scores.sort(key=lambda x: x["score"], reverse=True)
        return {
            "primary": w_scores[0] if len(w_scores) > 0 else {"name": "MP40", "ttk": 0.28},
            "secondary": w_scores[1] if len(w_scores) > 1 else (w_scores[0] if len(w_scores) > 0 else {"name": "GROZA", "ttk": 0.32})
        }
