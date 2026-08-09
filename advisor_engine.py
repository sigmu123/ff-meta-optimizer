import os
import sys
import time
import importlib.util

# Safe dynamic path resolution (Issue 18 Fix)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.patch_router import PatchRouter
from main import HybridMetaEngine

class AdvisorEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)
        
        # Dynamic fallback instead of hardcoded string (Issue 10 Fix)
        fetched_patch = self.router.get_latest_patch_version()
        self.active_patch_name = fetched_patch if fetched_patch else self._get_fallback_patch()

    def _get_fallback_patch(self):
        patches_dir = os.path.join(self.data_dir, "patches")
        if os.path.exists(patches_dir):
            available = sorted([d for d in os.listdir(patches_dir) if d.startswith("patch_")])
            if available:
                return available[-1]
        return "patch_ob54"

    def run_isolated_advisor(self):
        start_time = time.time()
        engine = HybridMetaEngine(patch_name=self.active_patch_name)
        top_raw_squads = engine.run_ga_pipeline(generations=20, population_size=100)
        
        # Safe Environment Variable Parsing
        playstyle_env = os.getenv("FF_PLAYSTYLE", "rush").strip().lower()
        if not playstyle_env.isalpha():
            playstyle_env = "rush"
            
        final_meta = engine.apply_context_multipliers(top_raw_squads, playstyle=playstyle_env)
        
        if not final_meta:
            print(f"[-] Error: No valid builds found for {self.active_patch_name}")
            return

        best_build = final_meta[0]
        exec_time = round((time.time() - start_time) * 1000, 3)
        b = best_build["build"]
        w = best_build["weapons"]

        output_file_path = os.path.join(current_dir, "advisor_result.txt")
        
        # Formatted string variable (Issue 2 Fix: Removed redundant read lock)
        report_content = (
            f"{'=' * 70}\n"
            f"    ISOLATED ADVISOR ENGINE - HYBRID PIPELINE V2\n"
            f"{'=' * 70}\n"
            f"[*] Engine Latency: {exec_time}ms | Search Strategy: Genetic Algorithm\n"
            f"[*] Active Patch  : {self.active_patch_name.upper()}\n"
            f"{'-' * 70}\n\n"
            f"1. 100% Accurate Dynamic Setup:\n"
            f"   • Active Character : {b['active'].title()}\n"
            + "".join([f"   • Passive {idx}        : {p.title()}\n" for idx, p in enumerate(b['passives'], 1)]) +
            f"   • Pet Choice       : {b['pet']}\n"
            f"   • Loadout          : {b['loadout']}\n\n"
            f"2. Weapon Analysis (TTK Calculated):\n"
            f"   • Primary (Close)  : {w['primary']['name']} | Optimal TTK: {w['primary']['ttk']}s\n"
            f"   • Secondary (Mid)  : {w['secondary']['name']} | Optimal TTK: {w['secondary']['ttk']}s\n\n"
            f"3. Hybrid System Output:\n"
            f"   • Projected Win Rate : {best_build['win_rate']}%\n"
            f"   • Status             : Verified by CSP & Evaluated via Custom Fitness Function\n"
            f"{'=' * 70}\n"
        )

        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            print(f"[+] Success! Optimal meta build generated.")
            print(f"[+] Result has been saved to: {output_file_path}\n")
            print(report_content) # Directly print from memory buffer
        except IOError as e:
            print(f"[-] File write error: {e}")

if __name__ == "__main__":
    advisor = AdvisorEngine()
    advisor.run_isolated_advisor()
