import os
import sys

# Ensure local imports resolve correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.append(current_dir)

from src.patch_router import PatchRouter
from patch_loader import PatchLoader
from engine.combinatorial_tester import PermutationTester
from interface.prompt_parser import PromptParser


def main():
    # 1. Initialize System Router & Load Active Patch Data
    router = PatchRouter(data_dir=os.path.join(current_dir, "data"))
    latest_patch = router.get_latest_patch_version() or "patch_v33"
    loader = PatchLoader(patch_name=latest_patch)

    # 2. Parse Execution Scenario (e.g., Clash Squad Rush Meta)
    parsed_intent = PromptParser.parse("OB34 CS Ranked rush build with high damage")

    # 3. Trigger Combinatorial Matrix Search Engine Across All Combinations
    tester = PermutationTester(patch_data=loader)
    optimization_results = tester.run_matrix_search(
        mode=parsed_intent.get("mode", "clash_squad"),
        playstyle=parsed_intent.get("playstyle", "rush"),
        top_k=1
    )

    best_build = optimization_results["top_build"]
    total_permutations = optimization_results["permutations_tested"]
    latency = optimization_results["latency_ms"]

    # 4. Standard Quick Execution Sheet UI Format
    print("=" * 60)
    print("          QUICK EXECUTION SHEET - META ENGINE OUTPUT          ")
    print("=" * 60)
    print(f"[*] Engine Latency: {latency:.3f}ms | Permutations Tested: {total_permutations}")
    print(f"[*] Active Isolated Patch: {str(latest_patch).upper()}")
    print("-" * 60)
    
    print("\n1. Setup EQUIP Karein (Direct Active/Passive/Pet/Loadout List):")
    print(f"   • Active Skill  : {best_build['character_loadout']['active_skill']}")
    print(f"   • Passive 1     : {best_build['character_loadout']['passives'][0]}")
    print(f"   • Passive 2     : {best_build['character_loadout']['passives'][1]}")
    print(f"   • Passive 3     : {best_build['character_loadout']['passives'][2]}")
    print(f"   • Pet Companion : {best_build['pet']}")
    print(f"   • Item Loadout  : {best_build['item_loadout']}")

    print("\n2. Weapons Multiplier (Recommended Guns):")
    print(f"   • Short-Range   : {best_build['weapons']['short_range']['name']}")
    print(f"     └ Eff Dmg: {best_build['weapons']['short_range']['effective_dmg']} HP | BTK: {best_build['weapons']['short_range']['btk']} | TTK: {best_build['weapons']['short_range']['ttk']}s")
    print(f"   • Mid-Range     : {best_build['weapons']['mid_range']['name']}")
    print(f"     └ Eff Dmg: {best_build['weapons']['mid_range']['effective_dmg']} HP | BTK: {best_build['weapons']['mid_range']['btk']} | TTK: {best_build['weapons']['mid_range']['ttk']}s")

    print("\n3. Strategic Winning Trick:")
    print(f"   • Step 1 (Defense) : {best_build['strategy']['defense_tactic']}")
    print(f"   • Step 2 (Attack)  : {best_build['strategy']['attack_tactic']}")
    print(f"   • Step 3 (Trick)   : {best_build['strategy']['map_trick']}")

    print("\n4. Simple Summary Result:")
    print(f"   • Defense Buff     : +{best_build['summary']['defense_buff_pct']}%")
    print(f"   • Attack Buff      : +{best_build['summary']['attack_buff_pct']}%")
    print(f"   • Win Probability  : {best_build['summary']['win_probability_pct']}%")
    print("=" * 60)


if __name__ == "__main__":
    main()
