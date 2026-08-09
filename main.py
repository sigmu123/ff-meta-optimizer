import os
import sys
import random
from core.ttk_calculator import TTKCalculator
from patch_loader import PatchLoader

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

class HybridMetaEngine:
    def __init__(self, patch_name="all"):
        self.loader = PatchLoader(patch_name=patch_name, base_dir=current_dir)
        self.ttk_calc = TTKCalculator()
        
        # Safely fallback if patches are empty
        self.actives = list(self.loader.active_skills.keys()) if self.loader.active_skills else ["alok"]
        self.passives = list(self.loader.passive_skills.keys()) if self.loader.passive_skills else ["kelly", "hayato", "moco"]
        self.weapons = self.loader.weapons if self.loader.weapons else {"mp40": {}, "groza": {}}
        self.pets = self.loader.pets if self.loader.pets else ["Rockie"]
        self.loadouts = self.loader.loadouts if self.loader.loadouts else ["Bonfire"]

    def _is_valid_chromosome(self, active, p1, p2, p3):
        passive_set = {p1, p2, p3}
        if len(passive_set) != 3: return False
        if active in passive_set: return False
        return True

    def _generate_random_valid_squad(self):
        while True:
            act = random.choice(self.actives)
            passives_sample = random.sample(self.passives, 3) if len(self.passives) >= 3 else self.passives * 3
            p1, p2, p3 = passives_sample[:3]
            if self._is_valid_chromosome(act, p1, p2, p3):
                return {
                    "active": act, 
                    "passives": sorted([p1, p2, p3]),
                    "pet": random.choice(self.pets),
                    "loadout": random.choice(self.loadouts)
                }

    def _fitness_function(self, squad):
        score = 50.0 
        act_name = str(squad["active"]).lower()
        passives = [str(p).lower() for p in squad["passives"]]
        
        if act_name == "tatsuya" and "kelly" in passives: score += 15.0  
        if act_name == "chrono" and str(squad["pet"]).lower() == "rockie": score += 10.0 
        if "hayato" in passives: score += 8.0 
        
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
            return parent1 
            
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
            
            if playstyle == "rush" and str(squad["loadout"]).lower() == "leg pockets": final_score += 2.5
            if playstyle == "sniper" and "moco" in squad["passives"]: final_score += 5.0
            
            best_weapons = self._get_optimal_weapons(squad)
            
            results.append({
                "build": squad,
                "win_rate": round(min(100.0, final_score), 2),
                "weapons": best_weapons
            })
            
        return sorted(results, key=lambda x: x["win_rate"], reverse=True)

    def _get_optimal_weapons(self, squad_context=None):
        w_scores = []
        for w_id, w_data in self.weapons.items():
            # Fix 4: Safeguard against bad schema causing float('inf') crashes
            if not isinstance(w_data, dict):
                continue
                
            stats = self.ttk_calc.calculate_weapon_ttk(w_data)
            
            if stats["ttk"] < 10 and stats["ttk"] != float('inf'): 
                score = (stats["effective_damage"] * 2) - (stats["ttk"] * 100)
                w_scores.append({"name": str(w_id).upper(), "ttk": stats["ttk"], "score": score})
        
        w_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Safe defaults if no viable weapon parsed
        return {
            "primary": w_scores[0] if w_scores else {"name": "MP40", "ttk": 0.28},
            "secondary": w_scores[1] if len(w_scores)>1 else {"name": "GROZA", "ttk": 0.32}
        }

if __name__ == "__main__":
    print("=" * 70)
    print("    HYBRID META OPTIMIZER ENGINE (CSP + GA + MULTIPLIERS)")
    print("=" * 70)
    
    engine = HybridMetaEngine(patch_name="all")
    print("[*] Running Genetic Search Space (Billions of combinations reduced)...")
    
    top_raw_squads = engine.run_ga_pipeline(generations=25, population_size=200, output_limit=10)
    
    playstyle_env = os.getenv("FF_PLAYSTYLE", "rush").lower()
    final_meta = engine.apply_context_multipliers(top_raw_squads, playstyle=playstyle_env)
    
    for rank, setup in enumerate(final_meta, 1):
        b = setup["build"]
        w = setup["weapons"]
        print(f"\n[ RANK #{rank} ] - Win Probability: {setup['win_rate']}%")
        print(f" ┣ Active  : {str(b['active']).title()}")
        print(f" ┣ Passive : {', '.join([str(p).title() for p in b['passives']])}")
        print(f" ┣ Utility : {str(b['pet']).title()} + {str(b['loadout']).title()}")
        print(f" ┗ Weapons : {w['primary']['name']} (TTK: {w['primary']['ttk']}s) & {w['secondary']['name']}")
