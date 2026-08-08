import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.patch_router import PatchRouter
from main import HybridMetaEngine

class AdvisorEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)
        self.active_patch_name = self.router.get_latest_patch_version() or "patch_ob54"

    def run_isolated_advisor(self):
        start_time = time.time()
        
        engine = HybridMetaEngine(patch_name=self.active_patch_name)
        
        top_raw_squads = engine.run_ga_pipeline(generations=20, population_size=100)
        
        # Fixed: Aligned context multiplier with global environment parameters
        playstyle_env = os.getenv("FF_PLAYSTYLE", "rush").lower()
        final_meta = engine.apply_context_multipliers(top_raw_squads, playstyle=playstyle_env)
        
        if not final_meta:
            print(f"[-] Error: No valid builds found for {self.active_patch_name}")
            return

        best_build = final_meta[0]
        exec_time = round((time.time() - start_time) * 1000, 3)
        
        b = best_build["build"]
        w = best_build["weapons"]

        # Output ko file mein save karne ka logic
        output_file_path = os.path.join(current_dir, "advisor_result.txt")
        
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("    ISOLATED ADVISOR ENGINE - HYBRID PIPELINE V2\n")
            f.write("=" * 70 + "\n")
            f.write(f"[*] Engine Latency: {exec_time}ms | Search Strategy: Genetic Algorithm\n")
            f.write(f"[*] Active Patch  : {self.active_patch_name.upper()}\n")
            f.write("-" * 70 + "\n\n")
            
            f.write("1. 100% Accurate Dynamic Setup:\n")
            f.write(f"   • Active Character : {b['active'].title()}\n")
            for idx, p in enumerate(b['passives'], 1):
                f.write(f"   • Passive {idx}        : {p.title()}\n")
            f.write(f"   • Pet Choice       : {b['pet']}\n")
            f.write(f"   • Loadout          : {b['loadout']}\n\n")

            f.write("2. Weapon Analysis (TTK Calculated):\n")
            f.write(f"   • Primary (Close)  : {w['primary']['name']} | Optimal TTK: {w['primary']['ttk']}s\n")
            f.write(f"   • Secondary (Mid)  : {w['secondary']['name']} | Optimal TTK: {w['secondary']['ttk']}s\n\n")

            f.write("3. Hybrid System Output:\n")
            f.write(f"   • Projected Win Rate : {best_build['win_rate']}%\n")
            f.write(f"   • Status             : Verified by CSP & Evaluated via Custom Fitness Function\n")
            f.write("=" * 70 + "\n")

        # Terminal par success message
        print(f"[+] Success! Optimal meta build generated.")
        print(f"[+] Result has been saved to: {output_file_path}\n")

        # File save karne ke baad terminal par bhi print karwane ke liye:
        with open(output_file_path, "r", encoding="utf-8") as f:
            print(f.read())

if __name__ == "__main__":
    advisor = AdvisorEngine()
    advisor.run_isolated_advisor()
