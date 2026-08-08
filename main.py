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
    def __init__(self, patch_name="patch_ob54"):
        self.loader = PatchLoader(patch_name=patch_name, base_dir=current_dir)
        self.ttk_calc = TTKCalculator()
        
        # Datasets
        self.actives = list(self.loader.active_skills.keys()) if self.loader.active_skills else ["alok", "chrono", "tatsuya", "wukong"]
        self.passives = list(self.loader.passive_skills.keys()) if self.loader.passive_skills else ["kelly", "hayato", "moco", "maxim", "shirou", "jota"]
        self.weapons = self.loader.weapons if self.loader.weapons else {"mp40": {"damage": 32, "rate_of_fire": 12}, "groza": {"damage": 38, "rate_of_fire": 10}}
        self.pets = ["Rockie", "Mr. Waggor", "Beaston", "Falco"]
        self.loadouts = ["Pocket Market", "Leg Pockets", "Bounty Token", "Bonfire"]

    # ==========================================
    # STAGE 1: CONSTRAINT PROGRAMMING (CSP)
    # ==========================================
    def _is_valid_chromosome(self, active, p1, p2, p3):
        """Filters out illegal combinations before they waste processing time"""
        passive_set = {p1, p2, p3}
        if len(passive_set) != 3: return False # No duplicate passives
        if active in passive_set: return False # Active cannot be in passives
        return True

    def _generate_random_valid_squad(self):
        while True:
            act = random.choice(self.actives)
            p1, p2, p3 = random.sample(self.passives, 3)
            if self._is_valid_chromosome(act, p1, p2, p3):
                return {
                    "active": act, 
                    "passives": [p1, p2, p3], 
                    "pet": random.choice(self.pets),
                    "loadout": random.choice(self.loadouts)
                }

    # ==========================================
    # STAGE 2: GENETIC ALGORITHM (GA) SEARCH
    # ==========================================
    def _fitness_function(self, squad):
        """Scoring logic based on synergy and CD overlaps"""
        score = 50.0 # Base win rate
        
        # Example Synergy Logic (Can be expanded using JSON data)
        act_name = squad["active"]
        passives = squad["passives"]
        
        if act_name == "tatsuya" and "kelly" in passives: score += 15.0  # Rush Synergy
        if act_name == "chrono" and "Rockie" == squad["pet"]: score += 10.0 # Cooldown Synergy
        if "hayato" in passives: score += 8.0 # Meta standard
        
        return min(99.9, score)

    def _crossover_and_mutate(self, parent1, parent2):
        child = {
            "active": parent1["active"] if random.random() > 0.5 else parent2["active"],
            "passives": parent1["passives"][:2] + [parent2["passives"][2]],
            "pet": parent1["pet"] if random.random() > 0.5 else parent2["pet"],
            "loadout": parent2["loadout"]
        }
        
        # Mutation
        if random.random() < 0.1: # 10% mutation rate
            child["active"] = random.choice(self.actives)
        
        # CSP Validation Fallback
        if not self._is_valid_chromosome(child["active"], *child["passives"]):
            return parent1 # Keep parent if mutation is illegal
            
        return child

    def run_ga_pipeline(self, generations=10, population_size=50):
        # 1. Init Population
        population = [self._generate_random_valid_squad() for _ in range(population_size)]
        
        for gen in range(generations):
            # Evaluate Fitness
            scored_pop = [(squad, self._fitness_function(squad)) for squad in population]
            scored_pop.sort(key=lambda x: x[1], reverse=True)
            
            # Selection (Top 50%)
            survivors = [x[0] for x in scored_pop[:population_size//2]]
            
            # Crossover to fill population
            next_gen = survivors.copy()
            while len(next_gen) < population_size:
                p1, p2 = random.sample(survivors, 2)
                next_gen.append(self._crossover_and_mutate(p1, p2))
                
            population = next_gen
            
        final_scored = [(squad, self._fitness_function(squad)) for squad in population]
        final_scored.sort(key=lambda x: x[1], reverse=True)
        return final_scored[:5] # Return Top 5

    # ==========================================
    # STAGE 3: DYNAMIC CONTEXT MULTIPLIERS
    # ==========================================
    def apply_context_multipliers(self, top_squads, playstyle="rush"):
        results = []
        for squad, base_score in top_squads:
            final_score = base_score
            
            # Playstyle Multipliers
            if playstyle == "rush" and squad["loadout"] == "Leg Pockets": final_score += 2.5
            if playstyle == "sniper" and "moco" in squad["passives"]: final_score += 5.0
            
            # Get Best Weapon Combos via TTK Math
            best_weapons = self._get_optimal_weapons()
            
            results.append({
                "build": squad,
                "win_rate": round(min(100.0, final_score), 2),
                "weapons": best_weapons
            })
            
        return sorted(results, key=lambda x: x["win_rate"], reverse=True)

    def _get_optimal_weapons(self):
        w_scores = []
        for w_id, w_data in self.weapons.items():
            stats = self.ttk_calc.calculate_weapon_ttk(w_data)
            if stats["ttk"] < 10: # Filter invalid
                score = (stats["effective_damage"] * 2) - (stats["ttk"] * 100)
                w_scores.append({"name": w_id.upper(), "ttk": stats["ttk"], "score": score})
        
        w_scores.sort(key=lambda x: x["score"], reverse=True)
        return {
            "primary": w_scores[0] if w_scores else {"name": "MP40", "ttk": 0.28},
            "secondary": w_scores[1] if len(w_scores)>1 else {"name": "GROZA", "ttk": 0.32}
        }

if __name__ == "__main__":
    print("=" * 70)
    print("    HYBRID META OPTIMIZER ENGINE (CSP + GA + MULTIPLIERS)")
    print("=" * 70)
    
    engine = HybridMetaEngine()
    print("[*] Running Genetic Search Space (Billions of combinations reduced)...")
    
    # Run the Pipeline
    top_raw_squads = engine.run_ga_pipeline(generations=15, population_size=100)
    final_meta = engine.apply_context_multipliers(top_raw_squads, playstyle="rush")
    
    for rank, setup in enumerate(final_meta, 1):
        b = setup["build"]
        w = setup["weapons"]
        print(f"\n[ RANK #{rank} ] - Win Probability: {setup['win_rate']}%")
        print(f" ┣ Active  : {b['active'].title()}")
        print(f" ┣ Passive : {', '.join([p.title() for p in b['passives']])}")
        print(f" ┣ Utility : {b['pet']} + {b['loadout']}")
        print(f" ┗ Weapons : {w['primary']['name']} (TTK: {w['primary']['ttk']}s) & {w['secondary']['name']}")
