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
        
        self.actives = list(self.loader.active_skills.keys()) if self.loader.active_skills else ["alok", "chrono", "k", "orion", "tatsuya"]
        self.passives = list(self.loader.passive_skills.keys()) if self.loader.passive_skills else ["kelly", "hayato", "moco", "jota", "andrew"]
        self.weapons = self.loader.weapons if self.loader.weapons else {"mp40": {"damage": 30, "rate_of_fire": 0.08}, "groza": {"damage": 38, "rate_of_fire": 0.12}}
        self.pets = self.loader.pets if self.loader.pets else ["Rockie", "Mr. Waggor", "Falco"]
        self.loadouts = self.loader.loadouts if self.loader.loadouts else ["Bonfire", "Leg Pockets", "Bounty Token"]

    def _is_valid_chromosome(self, active, p1, p2, p3):
        passive_set = {p1, p2, p3}
        if len(passive_set) != 3: 
            return False
        if active in passive_set: 
            return False
        return True

    def _generate_random_valid_squad(self):
        if len(self.passives) < 3:
            return {"active": self.actives[0], "passives": (self.passives * 3)[:3], "pet": self.pets[0], "loadout": self.loadouts[0]}
            
        attempts = 0
        while attempts < 100:
            act = random.choice(self.actives)
            p1, p2, p3 = random.sample(self.passives, 3)
            if self._is_valid_chromosome(act, p1, p2, p3):
                return {
                    "active": act, 
                    "passives": sorted([p1, p2, p3]),
                    "pet": random.choice(self.pets),
                    "loadout": random.choice(self.loadouts)
                }
            attempts += 1
        return {"active": self.actives[0], "passives": sorted(self.passives[:3]), "pet": self.pets[0], "loadout": self.loadouts[0]}

    def _fitness_function(self, squad):
        # Fully dynamic evaluation based on loaded weapon TTK metrics and stats
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
            child["active"] = random.choice(self.actives)
        
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
            if 0 < stats["ttk"] < 10: 
                dps = stats["effective_damage"] * (1 / max(0.01, stats.get("rate_of_fire", 0.2)))
                clean_name = str(w_id).split("_")[-1].upper()
                w_scores.append({"name": clean_name, "ttk": stats["ttk"], "score": dps})
        
        w_scores.sort(key=lambda x: x["score"], reverse=True)
        return {
            "primary": w_scores[0] if w_scores else {"name": "MP40", "ttk": 0.28},
            "secondary": w_scores[1] if len(w_scores) > 1 else {"name": "GROZA", "ttk": 0.32}
        }
