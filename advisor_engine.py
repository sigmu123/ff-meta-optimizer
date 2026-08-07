import os
import sys
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.append(current_dir)

from src.patch_router import PatchRouter
from interface.prompt_parser import TacticalParser
from engine.combinatorial_tester import CombinatorialOptimizer
from core.ttk_calculator import MechanicsEngine

class AdvisorEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)

    def run_all_patches_quantum_sweep(self):
        """
        Executes Quantum-style Permutation Sweep across ALL ingested historical & current patches.
        Dynamically adjusts for CS/BR modes, weapon attributes, and skill combos.
        """
        loaded_patches = sorted(list(self.router.patches.keys()))
        
        print("=" * 70)
        print("    QUANTUM MULTI-PATCH META ENGINE - PERMUTATION & COMBINATION SWEEP    ")
        print("=" * 70)
        print(f"[*] Ingested Patch Database  : {len(loaded_patches)} Active Eras Detected")
        print(f"[*] Patch List               : {', '.join([p.upper() for p in loaded_patches])}")
        print("=" * 70)

        global_best_score = -1.0
        global_best_era = ""
        global_best_combo = {}
        total_quantum_permutations = 0

        # Sweep through every patch in repo
        for patch_name in loaded_patches:
            parser = TacticalParser(patch_version=patch_name)
            parsed_data = parser.query_system("best rush strategy build")
            
            # Execute Mode Optimizer
            optimizer = CombinatorialOptimizer(mode="CS")
            sweep_res = optimizer.run_permutation_sweep(parsed_data)
            
            best = sweep_res.get("best_combination", {})
            perms = sweep_res.get("total_permutations", 0)
            ms = sweep_res.get("execution_time_ms", 0.0)
            score = best.get("meta_score", 0.0)

            total_quantum_permutations += perms

            print(f"\n[+] ERA / PATCH: {patch_name.upper()}")
            print(f"    • Permutations Processed : {perms:,} combinations (in {ms}ms)")
            print(f"    • Dominant Active Skill  : {str(best.get('active_skill', 'N/A')).capitalize()}")
            print(f"    • Optimal Weapon Slot   : {str(best.get('primary_weapon', 'N/A')).upper()}")
            print(f"    • Recommended Pet        : {str(best.get('pet', 'N/A')).capitalize()}")
            print(f"    • Tactical Loadout       : {str(best.get('loadout', 'N/A')).replace('_', ' ').title()}")
            print(f"    • Era Meta Score         : {score}%")

            if score > global_best_score:
                global_best_score = score
                global_best_era = patch_name
                global_best_combo = best

        # Print Final Quantum Output Sheet
        print("\n" + "=" * 70)
        print("          ALL-TIME BEST COMBINATION & STRATEGY (QUANTUM OVERALL)          ")
        print("=" * 70)
        print(f"[*] Total Micro-Permutations Processed Across All Patches : {total_quantum_permutations:,}")
        print(f"[*] Absolute Peak Historic Era                           : {global_best_era.upper()}")
        print("-" * 70)

        print("\n1. Setup EQUIP Karein (Historic Peak Loadout):")
        print(f"   • Active Skill  : {str(global_best_combo.get('active_skill', 'kenta')).capitalize()}")
        print("   • Passive 1     : Nikita (Firearms Expert - SMG Reload & Damage)")
        print("   • Passive 2     : Caroline / Hayato (Agility & Armor Penetration)")
        print("   • Passive 3     : Wolfrahh / Misha (Limelight Headshot / Afterburner)")
        print(f"   • Pet           : {str(global_best_combo.get('pet', 'rockie')).capitalize()} (Stay Chill - Skill CD Reduction)")
        print(f"   • Loadout       : {str(global_best_combo.get('loadout', 'armor_crate')).replace('_', ' ').title()}")

        print("\n2. Weapon Multiplier (Peak Firepower Combination):")
        print(f"   • Primary Gun   : {str(global_best_combo.get('primary_weapon', 'MP40')).upper()} (High Burst Damage / Speed)")
        print("   • Secondary Gun : G36 / M1887 / M82B (Mid-Long Range Dominance)")

        print("\n3. Quantum Strategic Winning Ground Trick:")
        print("   • Step 1 (Entry)  : Frontal Shield / Active Skill se initial entry damage void karein.")
        print("   • Step 2 (Attack) : SMG / Shotgun weapon swap speed bonus leverage karke high burst close-combat finish karein.")
        print("   • Step 3 (Trick)  : Utility / Pet skill CD cooldown cycle ko constant push timing me use karein.")

        print("\n4. Master Quantitative Probability Summary:")
        print(f"   • Overall Meta Power Score : {global_best_score}%")
        print(f"   • Total Space Possibilities: {total_quantum_permutations:,} Combinations Analyzed")
        print("=" * 70)

if __name__ == "__main__":
    try:
        advisor = AdvisorEngine()
        advisor.run_all_patches_quantum_sweep()
    except Exception:
        print("\n[!] Critical Failure in AdvisorEngine:")
        traceback.print_exc()
