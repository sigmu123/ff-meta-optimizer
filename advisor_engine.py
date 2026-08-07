import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.patch_router import PatchRouter
from core.ttk_calculator import MechanicsEngine
from patch_loader import PatchLoader

class AdvisorEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)
        
        self.active_patch_name = self.router.get_latest_patch_version() or "patch_ob54"
        self.loader = PatchLoader(patch_name=self.active_patch_name, base_dir=current_dir)

    def run_isolated_advisor(self):
        start_time = time.time()

        weapons = self.loader.weapons
        primary_weapon = "mp40"

        default_weapon = {"weapon_id": "mp40", "base_damage": 26, "rate_of_fire": 12.5}
        weapon_raw = weapons.get(primary_weapon, default_weapon)

        calc = MechanicsEngine(target_hp=200, target_vest_lvl=3, target_helmet_lvl=2)
        ttk_result = calc.calculate_weapon_ttk(weapon_raw, player_boosts={"damage_boost": 0.10})
        
        exec_time = round((time.time() - start_time) * 1000, 3)

        print("=" * 70)
        print("    ISOLATED META ADVISOR ENGINE - SINGLE PATCH MODE")
        print("=" * 70)
        print(f"[*] Engine Latency: {exec_time}ms")
        print(f"[*] Isolated Active Patch Target: {self.active_patch_name.upper()}")
        print("-" * 70)
        
        print("\n1. Dynamic Optimal Setup:")
        print("   • Active Skill  : Chrono (Time Turner)")
        print("   • Passive 1     : NIKITA")
        print("   • Passive 2     : OLIVIA")
        print("   • Passive 3     : MARO")
        print("   • Pet           : Rockie")
        print("   • Loadout       : Armor Crate")

        print("\n2. Weapon Analysis (Isolated Stats):")
        print(f"   • Primary Weapon: {primary_weapon.upper()} (Base Damage: {weapon_raw.get('base_damage', 26)})")
        print(f"   • Effective Dmg : {ttk_result['effective_damage']} HP | BTK: {ttk_result['btk']} | TTK: {ttk_result['ttk']}s")

        print("\n3. Meta Decision:")
        print(f"   • Status        : Successfully evaluated within {self.active_patch_name.upper()} context.")
        print("=" * 70)

if __name__ == "__main__":
    advisor = AdvisorEngine()
    advisor.run_isolated_advisor()
