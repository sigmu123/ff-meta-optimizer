import os
import sys
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.append(current_dir)

from src.patch_router import PatchRouter
from engine.combinatorial_tester import CombinatorialOptimizer

class AdvisorEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)

    def display_unified_quantum_output(self):
        """Passes all ingested patch datasets together to produce a purely dynamic merged combination strategy."""
        all_patches = self.router.patches
        loaded_patch_names = sorted(list(all_patches.keys()))

        optimizer = CombinatorialOptimizer(mode="CS")
        sweep_res = optimizer.run_global_cross_patch_sweep(all_patches)

        best = sweep_res.get("best_combination", {})
        exec_time = sweep_res.get("execution_time_ms", 0.0)
        total_perms = sweep_res.get("total_permutations", 0)
        entities = sweep_res.get("merged_entities_count", {})

        # Extract Dynamic Data Objects
        active_id = str(best.get("active_skill", "N/A")).upper()
        active_data = best.get("active_data", {})
        active_name = active_data.get("character_name", active_data.get("skill_name", active_id))
        active_type = active_data.get("type", "Active Combat")

        passives = [str(p).upper() for p in best.get("passives", [])]
        p1 = passives[0] if len(passives) > 0 else "N/A"
        p2 = passives[1] if len(passives) > 1 else "N/A"
        p3 = passives[2] if len(passives) > 2 else "N/A"

        weap_id = str(best.get("primary_weapon", "N/A")).upper()
        weap_data = best.get("weapon_data", {})
        weap_cat = weap_data.get("category", "Primary Weapon")
        weap_status = weap_data.get("status", "Standard Tier").title()

        pet_id = str(best.get("pet", "N/A")).title()
        loadout_id = str(best.get("loadout", "N/A")).replace("_", " ").title()

        print("=" * 70)
        print("          QUICK EXECUTION SHEET - QUANTUM CROSS-PATCH ENGINE          ")
        print("=" * 70)
        print(f"[*] Engine Latency: {exec_time}ms | Total Combinations Tested: {total_perms:,}")
        print(f"[*] Patches Combined ({len(loaded_patch_names)} Eras): {', '.join([p.upper() for p in loaded_patch_names])}")
        print(f"[*] Merged Entity Pool: {entities.get('active_skills', 0)} Actives | {entities.get('passive_skills', 0)} Passives | {entities.get('weapons', 0)} Weapons | {entities.get('pets', 0)} Pets")
        print("-" * 70)

        print("\n1. Dynamic Optimal Setup (Calculated Win Matrix):")
        print(f"   • Active Skill  : {active_name} ({active_type})")
        print(f"   • Passive 1     : {p1}")
        print(f"   • Passive 2     : {p2}")
        print(f"   • Passive 3     : {p3}")
        print(f"   • Pet           : {pet_id}")
        print(f"   • Loadout       : {loadout_id}")

        print("\n2. Weapons Multiplier (Matrix Evaluated Winner):")
        print(f"   • Primary Weapon: {weap_id} [{weap_cat} | Status: {weap_status}]")

        print("\n3. Quantum Decision Outcome:")
        print(f"   • Evaluated Permutations : {total_perms:,} Cross-Patch Combinations")
        print(f"   • Calculated Win Probability: {best.get('meta_score', 0.0)}% Score")
        print("=" * 70)

if __name__ == "__main__":
    try:
        advisor = AdvisorEngine()
        advisor.display_unified_quantum_output()
    except Exception:
        print("\n[!] Critical Failure in AdvisorEngine:")
        traceback.print_exc()
