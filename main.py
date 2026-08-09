import os
import sys
import random
from core.ttk_calculator import TTKCalculator
from patch_loader import PatchLoader

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class HybridMetaEngine:
    def __init__(self, patch_name="all"):
        self.loader = PatchLoader(patch_name=patch_name, base_dir=current_dir)
        self.ttk_calc = TTKCalculator()
        
        # Dynamic Fallbacks
        self.actives = list(self.loader.active_skills.keys()) if self.loader.active_skills else ["alok", "chrono", "k", "orion"]
        self.passives = list(self.loader.passive_skills.keys()) if self.loader.passive_skills else ["kelly", "hayato", "moco", "jota"]
        self.weapons = self.loader.weapons if self.loader.weapons else {"mp40": {}, "groza": {}}
        self.pets = self.loader.pets if self.loader.pets else ["Rockie", "Mr. Waggor"]
        self.loadouts = self.loader.loadouts if self.loader.loadouts else ["Bonfire", "Leg Pockets"]

    def _is_valid_chromosome(self, active, p1, p2, p3):
        passive_set = {p1, p2, p3}
        if len(passive_set) != 3: return False
        if active in passive_set: return False
        return True

    def _generate_random_valid_squad(self):
        if len(self.passives) < 3:
            return {"active": self.actives[0], "passives": self.passives * 3, "pet": self.pets[0], "loadout": self.loadouts[0]}
            
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
        return {"active": self.actives[0], "passives": self.passives[:3], "pet": self.pets[0], "loadout": self.loadouts[0]}

    def _fitness_function(self, squad):
        score = 50.0 
        act_name = str(squad["active"]).lower()
        passives = [str(p).lower() for p in squad["passives"]]
        
        if "tatsuya" in act_name and any("kelly" in p for p in passives): score *= 1.15  
        if "chrono" in act_name and "rockie" in str(squad["pet"]).lower(): score *= 1.10 
        if any("hayato" in p for p in passives): score *= 1.08 
        
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
            
            survivors = [x[0] for x in scored_pop[:population_size//2]]
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
            
            if playstyle == "rush" and str(squad["loadout"]).lower() == "leg pockets": final_score *= 1.05
            if playstyle == "sniper" and any("moco" in str(p).lower() for p in squad["passives"]): final_score *= 1.10
            
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
            if not isinstance(w_data, dict): continue
                
            stats = self.ttk_calc.calculate_weapon_ttk(w_data)
            if stats["ttk"] > 0 and stats["ttk"] < 10: 
                dps = (stats["effective_damage"] * (1 / max(0.01, stats.get("rate_of_fire", 0.2))))
                w_scores.append({"name": str(w_id).split("_")[-1].upper(), "ttk": stats["ttk"], "score": dps})
        
        w_scores.sort(key=lambda x: x["score"], reverse=True)
        return {
            "primary": w_scores[0] if w_scores else {"name": "MP40", "ttk": 0.28},
            "secondary": w_scores[1] if len(w_scores)>1 else {"name": "GROZA", "ttk": 0.32}
        }

if __name__ == "__main__":
    print("[+] Initializing Hybrid Meta Engine Direct Execution...")
    engine = HybridMetaEngine(patch_name="patch_ob54")
    raw_squads = engine.run_ga_pipeline(generations=15, population_size=50)
    playstyle = os.getenv("FF_PLAYSTYLE", "rush")
    results = engine.apply_context_multipliers(raw_squads, playstyle=playstyle)
    
    if results:
        top = results[0]
        print("\n" + "=" * 50)
        print(f" OPTIMAL META BUILD GENERATED ({playstyle.upper()})")
        print("=" * 50)
        print(f"Active Skill : {top['build']['active']}")
        print(f"Passives     : {', '.join(top['build']['passives'])}")
        print(f"Pet          : {top['build']['pet']}")
        print(f"Loadout      : {top['build']['loadout']}")
        print(f"Primary Gun  : {top['weapons']['primary']['name']} (TTK: {top['weapons']['primary']['ttk']}s)")
        print(f"Secondary    : {top['weapons']['secondary']['name']} (TTK: {top['weapons']['secondary']['ttk']}s)")
        print(f"Win Rate     : {top['win_rate']}%")
        print("=" * 50 + "\n")
