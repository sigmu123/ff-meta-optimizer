import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.patch_router import PatchRouter
from patch_loader import PatchLoader
from engine.combinatorial_tester import PermutationTester
from interface.prompt_parser import PromptParser

def process_patch(patch, parsed_intent):
    """Processes a single patch matrix search safely in a process worker."""
    try:
        loader = PatchLoader(patch_name=patch, base_dir=current_dir)
        
        if not loader.active_skills or not loader.passive_skills:
            return patch, None, 0, "Skipped (Data missing or empty)"

        tester = PermutationTester(patch_data=loader)
        results = tester.run_matrix_search(
            mode=parsed_intent.get("mode", "clash_squad"),
            playstyle=parsed_intent.get("playstyle", "rush"),
            top_k=1
        )
        tested_count = results.get("permutations_tested", 0) if results else 0
        return patch, results, tested_count, None
    except Exception as e:
        return patch, None, 0, str(e)

def main():
    print("=" * 70)
    print("      MULTI-PATCH OPTIMIZER (FAST PARALLEL EXECUTION)       ")
    print("=" * 70)

    router = PatchRouter(data_dir=os.path.join(current_dir, "data"))
    
    patches_dir = os.path.join(current_dir, "data", "patches")
    if os.path.exists(patches_dir):
        available_on_disk = set(os.listdir(patches_dir))
    else:
        available_on_disk = set()

    if hasattr(router, "get_all_available_patches"):
        raw_patches = router.get_all_available_patches()
    else:
        raw_patches = ["patch_v1", "patch_v2", "patch_v33_heroes_arise", "patch_rampage", "patch_5th_anniv", "patch_ob52", "patch_ob53", "patch_ob54"]

    all_patches = [p for p in raw_patches if p in available_on_disk]

    parsed_intent = PromptParser.parse("OB54 CS Ranked rush build with high damage")
    grand_total_permutations = 0

    print(f"[*] Starting matrix evaluation across {len(all_patches)} valid patches...\n")

    max_workers = min(os.cpu_count() or 4, len(all_patches))
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_patch, patch, parsed_intent): patch for patch in all_patches}
        
        for future in as_completed(futures):
            try:
                # Set strict 5-second per process limit
                patch, results, count, err = future.result(timeout=5.0)
                
                if err:
                    print(f"[-] PATCH: {str(patch).upper():<25} | Status: Error ({err})")
                    continue
                    
                if not results or "top_build" not in results or not results["top_build"]:
                    print(f"[-] PATCH: {str(patch).upper():<25} | Status: No valid build found")
                    continue

                grand_total_permutations += count
                best_build = results["top_build"]
                
                active_skill = best_build.get('character_loadout', {}).get('active_skill', 'N/A')
                win_prob = best_build.get('summary', {}).get('win_probability_pct', 'N/A')

                print(f"[+] PATCH: {str(patch).upper():<25} | Tested: {count:>8,} | Best Active: {active_skill:<12} | Win Rate: {win_prob}%")

            except Exception as exc:
                patch_name = futures[future]
                print(f"[-] PATCH: {str(patch_name).upper():<25} | Status: Timed out / Halted ({exc})")

    print("\n" + "=" * 70)
    print(f"[*] TOTAL COMBINATIONS EVALUATED: {grand_total_permutations:,}")
    print("=" * 70)

if __name__ == "__main__":
    main()
