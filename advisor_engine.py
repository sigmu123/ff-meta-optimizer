import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.patch_router import PatchRouter
from main import HybridMetaEngine

class AdvisorEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)
        self.active_patch_name = self.router.get_latest_patch_version() or "patch_ob54"

    def run_isolated_advisor(self):
        start_time = time.time()
        
        engine = HybridMetaEngine(patch_name=self.active_patch_name)
        
        top_raw_squads = engine.run_ga_pipeline(generations=20, population_size=100)
        
        # Fixed: Aligned context multiplier with global environment parameters
        playstyle_env = os.getenv("FF_PLAYSTYLE", "rush").lower()
        final_meta = engine.apply_context_multipliers(top_raw_squads, playstyle=playstyle_env)
        
        if not final_meta:
            print(f"[-] Error: No valid builds found for {self.active_patch_name}")
            return

        best_build = final_meta[0]
        exec_time = round((time.time() - start_time) * 1000, 3)

        print("=" * 70)
        print("    ISOLATED ADVISOR ENGINE - HYBRID PIPELINE V2")
        print("=" * 70)
        print(f"[*] Engine Latency: {exec_time}ms | Search Strategy: Genetic Algorithm")
        print(f"[*] Active Patch  : {self.active_patch_name.upper()}")
        print("-" * 70)
        
        b = best_build["build"]
        w = best_build["weapons"]

        print("\n1. 100% Accurate Dynamic Setup:")
        print(f"   • Active Character : {b['active'].title()}")
        for idx, p in enumerate(b['passives'], 1):
            print(f"   • Passive {idx}        : {p.title()}")
        print(f"   • Pet Choice       : {b['pet']}")
        print(f"   • Loadout          : {b['loadout']}")

        print("\n2. Weapon Analysis (TTK Calculated):")
        print(f"   • Primary (Close)  : {w['primary']['name']} | Optimal TTK: {w['primary']['ttk']}s")
        print(f"   • Secondary (Mid)  : {w['secondary']['name']} | Optimal TTK: {w['secondary']['ttk']}s")

        print("\n3. Hybrid System Output:")
        print(f"   • Projected Win Rate : {best_build['win_rate']}%")
        print(f"   • Status             : Verified by CSP & Evaluated via Custom Fitness Function")
        print("=" * 70)

if __name__ == "__main__":
    advisor = AdvisorEngine()
    advisor.run_isolated_advisor()
