import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.append(current_dir)

from src.patch_router import PatchRouter
from patch_loader import PatchLoader
from engine.combinatorial_tester import PermutationTester
from interface.prompt_parser import PromptParser


def main():
    router = PatchRouter(data_dir=os.path.join(current_dir, "data"))
    
    # Get all available patches in repo for cross-match analysis
    all_patches = router.get_all_available_patches() if hasattr(router, "get_all_available_patches") else ["patch_ob54", "patch_ob53", "patch_ob52"]
    
    parsed_intent = PromptParser.parse("OB54 CS Ranked rush build with high damage")

    print("=" * 70)
    print("      MULTI-PATCH CROSS-MATCH PERMUTATION MATRIX OPTIMIZER       ")
    print("=" * 70)

    grand_total_permutations = 0

    for patch in all_patches:
        loader = PatchLoader(patch_name=patch, base_dir=current_dir)
        tester = PermutationTester(patch_data=loader)
        
        results = tester.run_matrix_search(
            mode=parsed_intent.get("mode", "clash_squad"),
            playstyle=parsed_intent.get("playstyle", "rush"),
            top_k=1
        )
        
        best_build = results["top_build"]
        permutations_count = results["permutations_tested"]
        grand_total_permutations += permutations_count

        print(f"\n[+] PATCH: {str(patch).upper()} | Evaluated Combinations: {permutations_count}")
        print(f"    • Best Build Active  : {best_build['character_loadout']['active_skill']}")
        print(f"    • Passives Combination: {', '.join(best_build['character_loadout']['passives'])}")
        print(f"    • Primary Close Gun  : {best_build['weapons']['short_range']['name']} (TTK: {best_build['weapons']['short_range']['ttk']}s)")
        print(f"    • Secondary Mid Gun  : {best_build['weapons']['mid_range']['name']} (TTK: {best_build['weapons']['mid_range']['ttk']}s)")
        print(f"    • Pet / Loadout      : {best_build['pet']} / {best_build['item_loadout']}")
        print(f"    • Win Probability    : {best_build['summary']['win_probability_pct']}%")

    print("\n" + "=" * 70)
    print(f"[*] TOTAL PERMUTATIONS CROSS-MATCHED ACROSS ALL PATCHES: {grand_total_permutations}")
    print("=" * 70)


if __name__ == "__main__":
    main()
