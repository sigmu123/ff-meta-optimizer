import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.patch_router import PatchRouter
from patch_loader import PatchLoader
from engine.combinatorial_tester import PermutationTester
from interface.prompt_parser import PromptParser


def main():
    print("=" * 70)
    print("      MULTI-PATCH CROSS-MATCH PERMUTATION MATRIX OPTIMIZER       ")
    print("=" * 70)
    sys.stdout.flush()

    router = PatchRouter(data_dir=os.path.join(current_dir, "data"))
    
    # Get all available patches in repo for cross-match analysis
    if hasattr(router, "get_all_available_patches"):
        all_patches = router.get_all_available_patches()
    else:
        all_patches = ["patch_ob54", "patch_ob53", "patch_ob52"]

    parsed_intent = PromptParser.parse("OB54 CS Ranked rush build with high damage")

    grand_total_permutations = 0

    for patch in all_patches:
        try:
            loader = PatchLoader(patch_name=patch, base_dir=current_dir)
            tester = PermutationTester(patch_data=loader)
            
            results = tester.run_matrix_search(
                mode=parsed_intent.get("mode", "clash_squad"),
                playstyle=parsed_intent.get("playstyle", "rush"),
                top_k=1
            )
            
            if not results or "top_build" not in results or not results["top_build"]:
                print(f"\n[-] PATCH: {str(patch).upper()} | No combinations found.")
                continue

            best_build = results["top_build"]
            permutations_count = results.get("permutations_tested", 0)
            grand_total_permutations += permutations_count

            print(f"\n[+] PATCH: {str(patch).upper()} | Evaluated Combinations: {permutations_count}")
            
            active_skill = best_build.get('character_loadout', {}).get('active_skill', 'N/A')
            passives = ", ".join(best_build.get('character_loadout', {}).get('passives', []))
            
            sr = best_build.get('weapons', {}).get('short_range', {})
            mr = best_build.get('weapons', {}).get('mid_range', {})
            
            sr_name = sr.get('name', 'N/A') if isinstance(sr, dict) else 'N/A'
            sr_ttk = sr.get('ttk', 'N/A') if isinstance(sr, dict) else 'N/A'
            mr_name = mr.get('name', 'N/A') if isinstance(mr, dict) else 'N/A'
            mr_ttk = mr.get('ttk', 'N/A') if isinstance(mr, dict) else 'N/A'
            
            pet = best_build.get('pet', 'N/A')
            item = best_build.get('item_loadout', 'N/A')
            win_prob = best_build.get('summary', {}).get('win_probability_pct', 'N/A')

            print(f"    • Best Build Active  : {active_skill}")
            print(f"    • Passives Combination: {passives}")
            print(f"    • Primary Close Gun  : {sr_name} (TTK: {sr_ttk}s)")
            print(f"    • Secondary Mid Gun  : {mr_name} (TTK: {mr_ttk}s)")
            print(f"    • Pet / Loadout      : {pet} / {item}")
            print(f"    • Win Probability    : {win_prob}%")
            sys.stdout.flush()

        except Exception as e:
            print(f"\n[-] PATCH: {str(patch).upper()} | Skipping due to error: {e}")
            sys.stdout.flush()

    print("\n" + "=" * 70)
    print(f"[*] TOTAL PERMUTATIONS CROSS-MATCHED ACROSS ALL PATCHES: {grand_total_permutations}")
    print("=" * 70)


if __name__ == "__main__":
    main()
