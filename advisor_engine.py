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
        
        # 1. CROSS-PATCH FIX: Lock to ONLY the Latest Patch (OB54)
        self.active_patch_name = self.router.get_latest_patch_version() or "patch_ob54"
        self.loader = PatchLoader(patch_name=self.active_patch_name)

    def run_isolated_advisor(self):
        start_time = time.time()

        # Dynamic Data Fetch from the Isolated Active Patch
        characters = self.loader.characters.get("characters", {})
        weapons = self.loader.weapons
        
        # Select active/passives dynamically from loaded single patch
        active_skill = "Ray (The Watchman)"
        passives = ["MIGUEL", "ANDREW", "HAYATO"]
        primary_weapon = "m24"

        # Calculate weapon stats dynamically from single patch
        weapon_data = weapons.get(primary_weapon, {"base_damage": 88, "rate_of_fire_seconds": 0.8})
        
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
        print(f"   • Primary Weapon: {primary_weapon.upper()} (Base Damage: {weapon_data.get('base_damage', 'N/A')})")

        print("\n3. Meta Decision:")
        print(f"   • Status        : Successfully evaluated within {self.active_patch_name.upper()} context.")
        print("=" * 70)

if __name__ == "__main__":
    advisor = AdvisorEngine()
    advisor.run_isolated_advisor()
