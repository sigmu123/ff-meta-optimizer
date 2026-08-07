import os
import sys
import json
from concurrent.futures import ProcessPoolExecutor, as_completed

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.patch_router import PatchRouter
from patch_loader import PatchLoader
from engine.combinatorial_tester import PermutationTester
from interface.prompt_parser import PromptParser

def get_patch_timestamp(patch_dir, patch_name):
    """
    1. Folder ke andar metadata/manifest JSON me se release date check karta hai.
    2. Agar JSON na mile, to Real File System Modification Time (mtime) pick karta hai.
    """
    full_path = os.path.join(patch_dir, patch_name)
    
    # Priority 1: Check inside metadata.json / patch.json if it exists
    for meta_file in ["metadata.json", "patch.json", "info.json"]:
        json_path = os.path.join(full_path, meta_file)
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    if "release_timestamp" in data:
                        return data["release_timestamp"]
            except Exception:
                pass

    # Priority 2: Real System File Update Date & Time
    try:
        return os.path.getmtime(full_path)
    except Exception:
        return 0

def process_patch(patch, parsed_intent):
    """Processes a single patch matrix search safely in a process worker."""
    try:
        loader = PatchLoader(patch_name=patch, base_dir=current_dir)
        
        if not hasattr(loader, 'active_skills') or not loader.active_skills:
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
    print("=" * 75)
    print("   MULTI-PATCH CROSS-EVALUATION ENGINE (REAL DATE DETECTED)")
    print("=" * 75)

    patches_dir = os.path.join(current_dir, "data", "patches")
    
    if not os.path.exists(patches_dir):
        print("[-] Data patches directory not found.")
        return

    raw_folders = [f for f in os.listdir(patches_dir) if os.path.isdir(os.path.join(patches_dir, f))]

    # SORT BY REAL UPDATE DATE & TIME (Newest First)
    available_patches = sorted(
        raw_folders,
        key=lambda p: get_patch_timestamp(patches_dir, p),
        reverse=True
    )

    if not available_patches:
        print("[-] No valid patch folders found.")
        return

    parsed_intent = PromptParser.parse("CS Ranked rush build with high damage")
    
    print(f"[*] Total Patches Found : {len(available_patches)}")
    print(f"[*] Latest Patch Target : {available_patches[0].upper()} (Based on Real Update Time)\n")

    all_patch_results = {}
    grand_total_permutations = 0

    max_workers = min(os.cpu_count() or 4, len(available_patches))
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_patch, patch, parsed_intent): patch for patch in available_patches}
        
        for future in as_completed(futures):
            try:
                patch, results, count, err = future.result(timeout=5.0)
                if err:
                    print(f"[-] {str(patch).upper():<28} | Status: {err}")
                    continue
                
                if results and "top_build" in results:
                    grand_total_permutations += count
                    all_patch_results[patch] = results
                    print(f"[+] {str(patch).upper():<28} | Matrix Evaluated ({count:,} combos)")
            except Exception as exc:
                patch_name = futures[future]
                print(f"[-] {str(patch_name).upper():<28} | Timed out ({exc})")

    if not all_patch_results:
        print("\n[-] No valid build data extracted across patches.")
        return

    # Cross-Patch Strategy: Pick result from the latest updated patch folder
    latest_patch = available_patches[0]
    meta_build_data = all_patch_results.get(latest_patch) or list(all_patch_results.values())[0]
    best_build = meta_build_data["top_build"]

    print("\n" + "=" * 75)
    print(f"               LATEST META BUILD RECOMMENDATION ({latest_patch.upper()})")
    print("=" * 75)
    
    loadout = best_build.get("character_loadout", {})
    weapons = best_build.get("weapons", {})
    
    print(f" Active Skill   : {loadout.get('active_skill', 'N/A')}")
    print(f" Passive Skills  : {', '.join(loadout.get('passives', []))}")
    print(f" Pet             : {best_build.get('pet', 'N/A')}")
    print(f" Item Loadout    : {best_build.get('item_loadout', 'N/A')}")
    print("-" * 75)
    print(" Recommended Weapons:")
    print(f"   • Short Range : {weapons.get('short_range', {}).get('name', 'N/A')} (TTK: {weapons.get('short_range', {}).get('ttk', 'N/A')}s)")
    print(f"   • Mid/Long    : {weapons.get('mid_range', {}).get('name', 'N/A')} (TTK: {weapons.get('mid_range', {}).get('ttk', 'N/A')}s)")
    print("-" * 75)
    print(f" Win Rate Projection : {best_build.get('summary', {}).get('win_probability_pct', 'N/A')}%")
    print(f" Cross Combos Tested : {grand_total_permutations:,}")
    print("=" * 75)

if __name__ == "__main__":
    main()
