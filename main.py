import os
import sys
import random
import itertools
from core.ttk_calculator import TTKCalculator
from patch_loader import PatchLoader
from interface.prompt_parser import parse_full_prompt

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class HybridMetaEngine:
    def __init__(self, patch_name="patch_ob54", objective="max_damage", playstyle="rush", engagement_range="mid"):
        self.patch_name = patch_name
        self.loader = PatchLoader(patch_name=patch_name, base_dir=current_dir)
        self.ttk_calc = TTKCalculator()

        self._build_base_data()
        self._apply_patch_adjustments()

        self.objective = objective
        self.playstyle = playstyle
        self.engagement_range = engagement_range

    def _build_base_data(self):
        self.base_actives = {
            "alok": {"skill_name": "Drop the Beat", "type": "active", "cooldown": 45, "duration": 10, "heal": 5, "speed_boost": 15},
            "chrono": {"skill_name": "Time Turner", "type": "active", "cooldown": 60, "duration": 6, "shield_hp": 800},
            "k": {"skill_name": "Master of All", "type": "active", "cooldown": 3, "duration": 0, "ep_recovery": 3},
            "orion": {"skill_name": "Crimson Crush", "type": "active", "cooldown": 3, "duration": 3, "damage": 15},
            "tatsuya": {"skill_name": "Rebel Rush", "type": "active", "cooldown": 98, "duration": 0.3, "charges": 2},
            "steffie": {"skill_name": "Painted Refuge", "type": "active", "cooldown": 45, "duration": 10, "bullet_damage_reduction": 5, "explosive_damage_reduction": 15},
            "kenta": {"skill_name": "Swordsman's Wrath", "type": "active", "cooldown": 70, "duration": 5, "frontal_damage_reduction": 60},
        }
        self.base_passives = {
            "kelly": {"skill_name": "Dash", "type": "passive", "speed_boost": 6},
            "hayato": {"skill_name": "Art of Blades", "type": "passive", "armor_pen": 5},
            "moco": {"skill_name": "Hacker's Eye", "type": "passive", "mark_duration": 4},
            "jota": {"skill_name": "Sustained Raids", "type": "passive", "hp_on_hit": 5},
            "andrew": {"skill_name": "Armor Specialist", "type": "passive", "armor_reduction": 25},
            "antonio": {"skill_name": "Gangster's Spirit", "type": "passive", "extra_hp": 35},
            "kapella": {"skill_name": "Healing Song", "type": "passive", "heal_increase": 20, "revive_shield": 80},
            "olivia": {"skill_name": "Healing Touch", "type": "passive", "heal_spread": 80},
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

        self.actives = dict(self.base_actives)
        self.passives = dict(self.base_passives)
        self.weapons = dict(self.base_weapons)
        self.pets = list(self.base_pets)
        self.loadouts = list(self.base_loadouts)

    def _apply_patch_adjustments(self):
        for char_name, adjustments in self.loader.character_adjustments.items():
            for adj in adjustments:
                skill_name = adj.get("skill_name") or ""
                is_active = "active" in str(adj.get("type", "")).lower() or ("cooldown" in adj or "duration" in adj)
                if is_active:
                    if char_name.lower() in self.actives:
                        self._apply_character_adjustment(self.actives[char_name.lower()], adj)
                    else:
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

        for wep_name, adjustments in self.loader.weapon_adjustments.items():
            if wep_name.lower() in self.weapons:
                for adj in adjustments:
                    self._apply_weapon_adjustment(self.weapons[wep_name.lower()], adj)
            else:
                new_wep = {}
                for adj in adjustments:
                    self._apply_weapon_adjustment(new_wep, adj)
                if new_wep:
                    self.weapons[wep_name.lower()] = new_wep

        if self.loader.pets:
            for pet in self.loader.pets:
                if pet not in self.pets:
                    self.pets.append(pet)
        if self.loader.loadouts:
            for ld in self.loader.loadouts:
                if ld not in self.loadouts:
                    self.loadouts.append(ld)

    def _apply_character_adjustment(self, skill, adj):
        mapping = {
            "cooldown_seconds": "cooldown",
            "duration_seconds": "duration",
            "shield_hp": "shield_hp",
            "damage": "damage",
            "heal": "heal",
            "hp_recovery_per_second": "heal",
            "movement_speed_boost_percent": "speed_boost",
            "armor_penetration": "armor_pen",
            "bullet_damage_reduction": "bullet_damage_reduction",
            "explosive_damage_reduction": "explosive_damage_reduction",
            "frontal_damage_reduction": "frontal_damage_reduction",
            "armor_reduction": "armor_reduction",
            "extra_hp": "extra_hp",
            "hp_on_hit": "hp_on_hit",
            "heal_increase": "heal_increase",
            "revive_shield": "revive_shield",
            "heal_spread": "heal_spread",
        }
        for adj_key, skill_key in mapping.items():
            if adj_key in adj:
                skill[skill_key] = adj[adj_key]
        if "new_value" in adj:
            for k, v in adj.items():
                if k not in ["character_name", "skill_name", "type", "adjustment_type"]:
                    if isinstance(v, dict) and "new_value" in v:
                        skill[k] = v["new_value"]

    def _apply_weapon_adjustment(self, weapon, adj):
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
                        if "percentage" in adj_key or "%" in str(adj_key):
                            weapon[stat_key] *= (1 + val / 100.0)
                        else:
                            weapon[stat_key] += val
                    else:
                        weapon[stat_key] = val
        if "base_damage_percentage_change" in adj:
            if "damage" in weapon:
                weapon["damage"] *= (1 + adj["base_damage_percentage_change"] / 100.0)
        if "armor_penetration" in adj:
            weapon["armor_pen"] = adj["armor_penetration"]

    def _is_valid_chromosome(self, active, p1, p2, p3):
        passive_set = {p1, p2, p3}
        return len(passive_set) == 3 and active not in passive_set

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
        best_weapons = self._get_optimal_weapons(squad)
        if best_weapons["primary"]["ttk"] == float('inf'):
            return 0.0

        if self.objective == "max_damage":
            primary_dps = self._weapon_dps(best_weapons["primary"])
            secondary_dps = self._weapon_dps(best_weapons["secondary"])
            score = primary_dps + secondary_dps
            if self.playstyle == "rush" and squad.get("loadout", "").lower() == "leg pockets":
                score *= 1.05
            return score
        elif self.objective == "min_ttk":
            total_ttk = best_weapons["primary"]["ttk"] + best_weapons["secondary"]["ttk"]
            score = 100.0 / (total_ttk + 0.01)
            if self.playstyle == "rush" and squad.get("loadout", "").lower() == "leg pockets":
                score *= 1.05
            return score
        else:  # survival
            def_score = 0.0
            active_name = squad['active']
            active_skill = self.actives.get(active_name, {})
            shield_hp = active_skill.get("shield_hp", 0)
            bullet_dr = active_skill.get("bullet_damage_reduction", 0)
            explosive_dr = active_skill.get("explosive_damage_reduction", 0)
            frontal_dr = active_skill.get("frontal_damage_reduction", 0)
            heal = active_skill.get("heal", 0)

            for p in squad['passives']:
                pskill = self.passives.get(p, {})
                armor_reduction = pskill.get("armor_reduction", 0)
                extra_hp = pskill.get("extra_hp", 0)
                hp_on_hit = pskill.get("hp_on_hit", 0)
                heal_increase = pskill.get("heal_increase", 0)
                revive_shield = pskill.get("revive_shield", 0)
                heal_spread = pskill.get("heal_spread", 0)

                def_score += extra_hp
                total_dr = (armor_reduction + bullet_dr + explosive_dr + frontal_dr) / 100.0
                total_dr = min(total_dr, 0.8)
                def_score += heal + hp_on_hit + heal_increase * 0.5
                def_score += shield_hp * 0.1

            loadout = squad.get('loadout', '').lower()
            if loadout == "armor crate":
                def_score += 20
            elif loadout == "secret clue":
                def_score += 10
            elif loadout == "leg pockets":
                def_score += 5
            pet = squad.get('pet', '').lower()
            if pet == "ottero":
                def_score += 10

            def_score = max(1.0, def_score)
            return def_score

    def _weapon_dps(self, weapon_info):
        w_name = weapon_info["name"].lower()
        for w_id, w_data in self.weapons.items():
            if w_id.endswith(w_name) or w_id.split("_")[-1] == w_name:
                stats = self.ttk_calc.calculate_weapon_ttk(w_data)
                if stats and stats["ttk"] < float('inf'):
                    dps = stats["effective_damage"] * (1.0 / max(0.01, stats.get("rate_of_fire", 0.2)))
                    return dps
        return 0.0

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
        for _ in range(generations):
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
        seen = set()
        for squad, score in final_scored:
            sig = (squad["active"], tuple(squad["passives"]), squad["pet"], squad["loadout"])
            if sig not in seen:
                seen.add(sig)
                unique_squads.append((squad, score))
            if len(unique_squads) == output_limit:
                break
        return unique_squads

    def run_exhaustive_search(self, output_limit=10, max_combinations=None):
        active_list = list(self.actives.keys())
        passive_list = list(self.passives.keys())
        pet_list = self.pets
        loadout_list = self.loadouts
        weapon_keys = list(self.weapons.keys())

        if len(passive_list) < 3:
            raise ValueError("Not enough passives to choose 3.")

        passive_combos = list(itertools.combinations(passive_list, 3))
        combos = []
        if max_combinations is not None and len(active_list)*len(passive_combos)*len(pet_list)*len(loadout_list)*len(weapon_keys)*len(weapon_keys) > max_combinations:
            for _ in range(max_combinations):
                act = random.choice(active_list)
                p_combo = random.choice(passive_combos)
                while act in p_combo:
                    act = random.choice(active_list)
                pet = random.choice(pet_list)
                loadout = random.choice(loadout_list)
                primary = random.choice(weapon_keys)
                secondary = random.choice([w for w in weapon_keys if w != primary])
                combos.append((act, p_combo, pet, loadout, primary, secondary))
        else:
            for act in active_list:
                for p_combo in passive_combos:
                    if act in p_combo:
                        continue
                    for pet in pet_list:
                        for loadout in loadout_list:
                            for primary in weapon_keys:
                                for secondary in weapon_keys:
                                    if primary != secondary:
                                        combos.append((act, p_combo, pet, loadout, primary, secondary))

        scored = []
        for (act, p_combo, pet, loadout, primary, secondary) in combos:
            squad = {
                "active": act,
                "passives": list(p_combo),
                "pet": pet,
                "loadout": loadout
            }
            score = self._fitness_for_weapons(squad, primary, secondary)
            scored.append((squad, score, primary, secondary))

        scored.sort(key=lambda x: x[1], reverse=True)
        unique = []
        seen = set()
        for squad, score, prim, sec in scored:
            sig = (squad["active"], tuple(squad["passives"]), squad["pet"], squad["loadout"])
            if sig not in seen:
                seen.add(sig)
                unique.append((squad, score, prim, sec))
            if len(unique) == output_limit:
                break

        result = []
        for squad, score, prim, sec in unique:
            primary_info = self._weapon_info(prim)
            secondary_info = self._weapon_info(sec)
            win_rate = min(99.99, (score / 200.0) * 100)
            result.append({
                "build": squad,
                "win_rate": round(win_rate, 2),
                "weapons": {
                    "primary": primary_info,
                    "secondary": secondary_info
                },
                "raw_score": score
            })
        return result

    def _fitness_for_weapons(self, squad, primary_key, secondary_key):
        prim_stats = self.ttk_calc.calculate_weapon_ttk(self.weapons[primary_key])
        sec_stats = self.ttk_calc.calculate_weapon_ttk(self.weapons[secondary_key])
        if prim_stats["ttk"] == float('inf') or sec_stats["ttk"] == float('inf'):
            return 0.0

        if self.objective == "max_damage":
            prim_dps = prim_stats["effective_damage"] * (1.0 / max(0.01, prim_stats.get("rate_of_fire", 0.2)))
            sec_dps = sec_stats["effective_damage"] * (1.0 / max(0.01, sec_stats.get("rate_of_fire", 0.2)))
            score = prim_dps + sec_dps
            if self.playstyle == "rush" and squad.get("loadout", "").lower() == "leg pockets":
                score *= 1.05
            return score
        elif self.objective == "min_ttk":
            total_ttk = prim_stats["ttk"] + sec_stats["ttk"]
            score = 100.0 / (total_ttk + 0.01)
            if self.playstyle == "rush" and squad.get("loadout", "").lower() == "leg pockets":
                score *= 1.05
            return score
        else:  # survival
            def_score = self._fitness_function(squad)
            total_ttk = prim_stats["ttk"] + sec_stats["ttk"]
            ttk_score = 100.0 / (total_ttk + 0.01)
            def_score_scaled = min(100, def_score * 0.5)
            combined = 0.7 * def_score_scaled + 0.3 * ttk_score
            return combined

    def _weapon_info(self, weapon_key):
        stats = self.ttk_calc.calculate_weapon_ttk(self.weapons[weapon_key])
        clean_name = str(weapon_key).split("_")[-1].upper()
        return {"name": clean_name, "ttk": stats["ttk"]}

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
        if len(w_scores) >= 2:
            return {"primary": w_scores[0], "secondary": w_scores[1]}
        else:
            return {"primary": w_scores[0] if w_scores else {"name": "MP40", "ttk": 0.28},
                    "secondary": w_scores[0] if w_scores else {"name": "GROZA", "ttk": 0.32}}

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
