import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.patch_router import PatchRouter
from core.ttk_calculator import MechanicsEngine
from patch_loader import PatchLoader
from engine.combinatorial_tester import PermutationTester

class AdvisorEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)
        self.active_patch_name = self.router.get_latest_patch_version() or "patch_ob54"
        self.loader = PatchLoader(patch_name=self.active_patch_name, base_dir=current_dir)

    def run_isolated_advisor(self):
        start_time = time.time()

        tester = PermutationTester(patch_data=self.loader)
        results = tester.run_matrix_search(mode="clash_squad", playstyle="rush", top_k=1)
        
        best_build = results["top_build"]
        exec_time = round((time.time() - start_time) * 1000, 3)

        print("=" * 70)
        print("    ISOLATED META ADVISOR ENGINE - SINGLE PATCH MODE")
        print("=" * 70)
        print(f"[*] Engine Latency: {exec_time}ms | Permutations Evaluated: {results['permutations_tested']}")
        print(f"[*] Isolated Active Patch Target: {self.active_patch_name.upper()}")
        print("-" * 70)
        
        print("\n1. Dynamic Optimal Setup (Evaluated Mathematically):")
        print(f"   • Active Skill  : {best_build['character_loadout']['active_skill']}")
        for idx, p in enumerate(best_build['character_loadout']['passives'], 1):
            print(f"   • Passive {idx}     : {p}")
        print(f"   • Pet           : {best_build['pet']}")
        print(f"   • Loadout       : {best_build['item_loadout']}")

        print("\n2. Weapon Analysis (Calculated Real Stats):")
        sr = best_build['weapons']['short_range']
        mr = best_build['weapons']['mid_range']
        print(f"   • Primary (Close) : {sr['name']} | Eff Dmg: {sr['effective_dmg']} HP | BTK: {sr['btk']} | TTK: {sr['ttk']}s")
        print(f"   • Secondary (Mid) : {mr['name']} | Eff Dmg: {mr['effective_dmg']} HP | BTK: {mr['btk']} | TTK: {mr['ttk']}s")

        print("\n3. Calculated Meta Decision:")
        print(f"   • Projected Win Rate : {best_build['summary']['win_probability_pct']}%")
        print(f"   • Status             : Validated under active parameters of {self.active_patch_name.upper()}")
        print("=" * 70)

if __name__ == "__main__":
    advisor = AdvisorEngine()
    advisor.run_isolated_advisor()
