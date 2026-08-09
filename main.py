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

        self.objective = objective          # "max_damage", "min_ttk", or "survival"
        self.playstyle = playstyle
        self.engagement_range = engagement_range

    def _build_base_data(self):
        # Same as before, but we now include more defensive attributes in base sets
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

    # ----------------------------------------------------------------------
    # (The rest of the methods: _apply_patch_adjustments, _apply_character_adjustment,
    #  _apply_weapon_adjustment, _is_valid_chromosome, _generate_random_valid_squad,
    #  _weapon_dps, _crossover_and_mutate, run_ga_pipeline remain exactly as before)
    # ----------------------------------------------------------------------

    # We only change _fitness_function, _fitness_for_weapons, and run_exhaustive_search.

    def _fitness_function(self, squad):
        """
        Compute fitness based on objective.
        For 'survival', compute a defensive score based on:
          - Effective HP (base HP + shield HP)
          - Damage reduction from passives (armor_reduction, frontal_damage_reduction)
          - Healing potential (hp_on_hit, heal, heal_increase)
          - Loadout bonuses (Armor Crate, etc.)
        """
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
            # Gather defensive attributes from active, passives, loadout
            def_score = 0.0
            active_name = squad['active']
            active_skill = self.actives.get(active_name, {})
            # Shield HP (e.g., Chrono)
            shield_hp = active_skill.get("shield_hp", 0)
            # Duration of shield (for uptime)
            shield_duration = active_skill.get("duration", 0)
            # Damage reduction (Steffie, Kenta)
            bullet_dr = active_skill.get("bullet_damage_reduction", 0)
            explosive_dr = active_skill.get("explosive_damage_reduction", 0)
            frontal_dr = active_skill.get("frontal_damage_reduction", 0)
            # Healing from active (Alok)
            heal = active_skill.get("heal", 0)

            # Passives
            for p in squad['passives']:
                pskill = self.passives.get(p, {})
                # Armor reduction (Andrew)
                armor_reduction = pskill.get("armor_reduction", 0)
                # Extra HP (Antonio)
                extra_hp = pskill.get("extra_hp", 0)
                # HP on hit (Jota)
                hp_on_hit = pskill.get("hp_on_hit", 0)
                # Healing increase (Kapella)
                heal_increase = pskill.get("heal_increase", 0)
                # Revive shield (Kapella)
                revive_shield = pskill.get("revive_shield", 0)
                # Heal spread (Olivia)
                heal_spread = pskill.get("heal_spread", 0)

                # Accumulate defensive values
                # Effective HP: base (200) + extra_hp + shield_hp (if any)
                def_score += extra_hp
                # Damage reduction: armor_reduction reduces incoming damage (e.g., 25% reduction)
                # We'll treat it as a percentage reduction to effective damage taken
                # We'll sum reductions (capped at 80% to avoid absurd)
                total_dr = (armor_reduction + bullet_dr + explosive_dr + frontal_dr) / 100.0
                total_dr = min(total_dr, 0.8)
                # Healing potential: heal + hp_on_hit + heal_increase
                def_score += heal + hp_on_hit + heal_increase * 0.5  # weight
                # Shield HP from active adds to effective HP
                def_score += shield_hp * 0.1  # weight for shield HP (since it's temporary)
                # Loadout bonuses
                loadout = squad.get('loadout', '').lower()
                if loadout == "armor crate":
                    def_score += 20  # armor repair value
                elif loadout == "secret clue":
                    def_score += 10  # EP conversion for healing
                elif loadout == "leg pockets":
                    def_score += 5   # extra gloo walls for cover
                # Pet bonuses (if any defensive)
                pet = squad.get('pet', '').lower()
                if pet == "ottero":
                    def_score += 10  # EP restore on heal

            # Normalize score (higher is better)
            # Scale to similar range as damage scores (around 100-200)
            def_score = max(1.0, def_score)
            # Also consider weapon's defensive capabilities? Not directly.
            # For now, return def_score (larger is better)
            return def_score

    def _fitness_for_weapons(self, squad, primary_key, secondary_key):
        """Compute fitness for given weapons, respecting objective."""
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
            # For survival, we still want reasonable TTK but prioritize defensive build
            # We'll combine defensive score (from squad) and TTK penalty
            def_score = self._fitness_function(squad)  # already computed
            # Penalize bad TTK (higher TTK lowers score)
            total_ttk = prim_stats["ttk"] + sec_stats["ttk"]
            ttk_score = 100.0 / (total_ttk + 0.01)
            # Blend: defensive score (70%) + TTK (30%)
            # Scale def_score to similar range
            def_score_scaled = min(100, def_score * 0.5)
            combined = 0.7 * def_score_scaled + 0.3 * ttk_score
            return combined

    def _weapon_info(self, weapon_key):
        stats = self.ttk_calc.calculate_weapon_ttk(self.weapons[weapon_key])
        clean_name = str(weapon_key).split("_")[-1].upper()
        return {"name": clean_name, "ttk": stats["ttk"]}

    # ---- Exhaustive Search (UPDATED to avoid duplicate weapons) ----
    def run_exhaustive_search(self, output_limit=10, max_combinations=None):
        active_list = list(self.actives.keys())
        passive_list = list(self.passives.keys())
        pet_list = self.pets
        loadout_list = self.loadouts
        weapon_keys = list(self.weapons.keys())

        if len(passive_list) < 3:
            raise ValueError("Not enough passives to choose 3.")

        passive_combos = list(itertools.combinations(passive_list, 3))

        # Build combinations ensuring primary != secondary
        combos = []
        if max_combinations is not None:
            sample_size = max_combinations
            # random sampling
            for _ in range(sample_size):
                act = random.choice(active_list)
                p_combo = random.choice(passive_combos)
                while act in p_combo:
                    act = random.choice(active_list)
                pet = random.choice(pet_list)
                loadout = random.choice(loadout_list)
                # Pick two different weapons
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
            # Winrate estimation: just a rough mapping
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

    # ---- Existing methods (unchanged except for above) ----
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
        # Ensure primary and secondary are different if possible
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

    # (The rest of the methods: _apply_patch_adjustments, _apply_character_adjustment, _apply_weapon_adjustment,
    #  _is_valid_chromosome, _generate_random_valid_squad, _weapon_dps, _crossover_and_mutate, run_ga_pipeline
    #  remain exactly as in the original file, so we don't duplicate them here for brevity,
    #  but they must be included in the final file.)
