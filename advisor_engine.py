import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.patch_router import PatchRouter
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
        
        if not results or "top_build" not in results or not results["top_build"]:
            print(f"[-] Error: No valid build options found for patch {self.active_patch_name}")
            return

        best_build = results["top_build"]
        exec_time = round((time.time() - start_time) * 1000, 3)

        print("=" * 70)
        print("    ISOLATED META ADVISOR ENGINE - SINGLE PATCH MODE")
        print("=" * 70)
        print(f"[*] Engine Latency: {exec_time}ms | Permutations Evaluated: {results.get('permutations_tested', 0)}")
        print(f"[*] Isolated Active Patch Target: {self.active_patch_name.upper()}")
        print("-" * 70)
        
        loadout = best_build.get('character_loadout', {})
        print("\n1. Dynamic Optimal Setup (Evaluated Mathematically):")
        print(f"   • Active Skill  : {loadout.get('active_skill', 'N/A')}")
        for idx, p in enumerate(loadout.get('passives', []), 1):
            print(f"   • Passive {idx}     : {p}")
        print(f"   • Pet           : {best_build.get('pet', 'N/A')}")
        print(f"   • Loadout       : {best_build.get('item_loadout', 'N/A')}")

        print("\n2. Weapon Analysis (Calculated Real Stats):")
        weapons = best_build.get('weapons', {})
        sr = weapons.get('short_range', {})
        mr = weapons.get('mid_range', {})
        print(f"   • Primary (Close) : {sr.get('name', 'N/A')} | Eff Dmg: {sr.get('effective_dmg', 0)} HP | BTK: {sr.get('btk', 0)} | TTK: {sr.get('ttk', 0)}s")
        print(f"   • Secondary (Mid) : {mr.get('name', 'N/A')} | Eff Dmg: {mr.get('effective_dmg', 0)} HP | BTK: {mr.get('btk', 0)} | TTK: {mr.get('ttk', 0)}s")

        print("\n3. Calculated Meta Decision:")
        summary = best_build.get('summary', {})
        print(f"   • Projected Win Rate : {summary.get('win_probability_pct', 'N/A')}%")
        print(f"   • Status             : Validated under active parameters of {self.active_patch_name.upper()}")
        print("=" * 70)

if __name__ == "__main__":
    advisor = AdvisorEngine()
    advisor.run_isolated_advisor()
