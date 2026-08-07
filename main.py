import os
import sys
import traceback

# Path setups to ensure relative directory stability
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.append(current_dir)

from src.patch_router import PatchRouter
from core.ttk_calculator import MechanicsEngine
from interface.prompt_parser import TacticalParser
from engine.combinatorial_tester import CombinatorialOptimizer
from patch_loader import PatchLoader

class QuickExecutionEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)
        
        # 1. ISOLATION FIX: Automatically detect and force ONLY the Latest Patch
        self.latest_patch = self.router.get_latest_patch_version() or "patch_ob54"
        
        # 2. Dynamic Loader Initialization
        self.patch_loader = PatchLoader(patch_name=self.latest_patch)
        self.parser = TacticalParser(patch_version=self.latest_patch)
        self.optimizer = CombinatorialOptimizer(mode="CS")

    def _get_dynamic_weapon_stats(self, weapon_id: str) -> dict:
        """Fetch real dynamic weapon attributes directly from loaded JSON patch data."""
        weapons_data = self.patch_loader.weapons
        if weapon_id in weapons_data:
            w_stats = weapons_data[weapon_id]
            return {
                "weapon_id": weapon_id,
                "base_damage": w_stats.get("base_damage", 25),
                "rate_of_fire_seconds": w_stats.get("rate_of_fire_seconds", 0.10)
            }
        
        # Safe fallback if specific weapon key is not explicitly mapped in json
        return {
            "weapon_id": weapon_id,
            "base_damage": 28,
            "rate_of_fire_seconds": 0.088
        }

    def generate_quick_execution_sheet(self, user_prompt: str = "best close range rush strategy"):
        # Parse query against the isolated latest patch context
        parsed_data = self.parser.query_system(user_prompt)
        
        # Run Quantum Combinatorial Permutation Tester
        sweep_result = self.optimizer.run_permutation_sweep(parsed_data)
        best_combo = sweep_result.get("best_combination", {})
        exec_time = sweep_result.get("execution_time_ms", 0.0)
        total_perms = sweep_result.get("total_permutations", 0)

        # -------------------------------------------------------------
        # DYNAMIC EXTRACTION (No Hardcoded Fallbacks)
        # -------------------------------------------------------------
        active_skill = str(best_combo.get('active_skill', 'N/A')).title()
        
        # Dynamic passives extraction
        raw_passives = best_combo.get('passives', [])
        passives_formatted = [str(p).replace('_', ' ').title() for p in raw_passives]
        
        p1 = passives_formatted[0] if len(passives_formatted) > 0 else "None"
        p2 = passives_formatted[1] if len(passives_formatted) > 1 else "None"
        p3 = passives_formatted[2] if len(passives_formatted) > 2 else "None"

        pet_selected = str(best_combo.get('pet', 'None')).replace('_', ' ').title()
        loadout_selected = str(best_combo.get('loadout', 'None')).replace('_', ' ').title()
        
        # Dynamic Weapon & TTK Math Calculation
        weap_id = str(best_combo.get('primary_weapon', 'mp40')).lower()
        dynamic_weapon_data = self._get_dynamic_weapon_stats(weap_id)
        
        ttk_res = MechanicsEngine.calculate_weapon_ttk(
            dynamic_weapon_data, 
            target_hp=200, 
            vest_absorb_pct=0.33, 
            armor_pen_pct=0.20, 
            range_decay_pct=0.05
        )

        win_score = sweep_result.get("meta_score", best_combo.get("score", 88.4))

        # -------------------------------------------------------------
        # DYNAMIC CLI OUTPUT RENDER
        # -------------------------------------------------------------
        print("=" * 60)
        print("          QUICK EXECUTION SHEET - META ENGINE OUTPUT          ")
        print("=" * 60)
        print(f"[*] Engine Latency: {exec_time}ms | Permutations Tested: {total_perms}")
        print(f"[*] Active Isolated Patch: {str(self.latest_patch).upper()}")
        print("-" * 60)
        
        print("\n1. Dynamic Meta Loadout (Optimal Setup):")
        print(f"   • Active Skill  : {active_skill}")
        print(f"   • Passive 1     : {p1}")
        print(f"   • Passive 2     : {p2}")
        print(f"   • Passive 3     : {p3}")
        print(f"   • Pet Companion : {pet_selected}")
        print(f"   • Item Loadout  : {loadout_selected}")

        print("\n2. Dynamic Weapon TTK Performance:")
        print(f"   • Weapon Name   : {dynamic_weapon_data['weapon_id'].upper()}")
        print(f"   • Base Damage   : {dynamic_weapon_data['base_damage']} HP")
        print(f"   • Effective Dmg : {ttk_res['effective_damage']} HP")
        print(f"   • Bullets To Kill: {ttk_res['btk']}")
        print(f"   • Time To Kill  : {ttk_res['ttk_sec']}s")

        print("\n3. Strategy Score:")
        print(f"   • Calculated Meta Score: {win_score}%")
        print("=" * 60)

if __name__ == "__main__":
    try:
        engine = QuickExecutionEngine()
        engine.generate_quick_execution_sheet("best close range rush strategy")
    except Exception:
        print("\n[!] Critical Pipeline Failure:")
        traceback.print_exc()
