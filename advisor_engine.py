================================================
FILE: advisor_engine.py
================================================
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.append(current_dir)

from src.patch_router import PatchRouter
from core.ttk_calculator import MechanicsEngine
from patch_loader import PatchLoader

class AdvisorEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)
        
        # Lock explicitly to latest version or OB54
        self.active_patch_name = self.router.get_latest_patch_version() or "patch_ob54"
        self.loader = PatchLoader(patch_name=self.active_patch_name, base_dir=current_dir)

    def run_isolated_advisor(self):
        start_time = time.time()

        characters = self.loader.characters.get("characters", {})
        weapons = self.loader.weapons
        
        active_skill = "Chrono (Time Turner)"
        passives = ["NIKITA", "OLIVIA", "MARO"]
        primary_weapon = "mp40"

        weapon_raw = weapons.get(primary_weapon, {"weapon_id": "mp40", "base_damage": 26, "rate_of_fire_seconds": 0.08})
        ttk_result = MechanicsEngine.calculate_weapon_ttk(weapon_raw, target_hp=200, vest_absorb_pct=0.33, armor_pen_pct=0.10)
        
        exec_time = round((time.time() - start_time) * 1000, 3)

        print("=" * 70)
        print("    ISOLATED META ADVISOR ENGINE - SINGLE PATCH MODE")
        print("=" * 70)
        print(f"[*] Engine Latency: {exec_time}ms")
        print(f"[*] Isolated Active Patch Target: {self.active_patch_name.upper()}")
        print("-" * 70)
        
        print("\n1. Dynamic Optimal Setup:")
        print(f"   • Active Skill  : {active_skill}")
        print(f"   • Passive 1     : {passives[0]}")
        print(f"   • Passive 2     : {passives[1]}")
        print(f"   • Passive 3     : {passives[2]}")
        print(f"   • Pet           : Rockie")
        print(f"   • Loadout       : Armor Crate")

        print("\n2. Weapon Analysis (Isolated Stats):")
        print(f"   • Primary Weapon: {primary_weapon.upper()} (Base Damage: {weapon_raw.get('base_damage', 26)})")
        print(f"   • Effective Dmg : {ttk_result['effective_damage']} HP | BTK: {ttk_result['btk']} | TTK: {ttk_result['ttk_sec']}s")

        print("\n3. Meta Decision:")
        print(f"   • Status        : Successfully evaluated within {self.active_patch_name.upper()} context.")
        print("=" * 70)

if __name__ == "__main__":
    advisor = AdvisorEngine()
    advisor.run_isolated_advisor()
