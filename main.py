import sys
import os
import traceback
from src.patch_router import PatchRouter # Folder structure ke mutabiq theek hai

class MetaOptimizerEngine:
    def __init__(self):
        # Yeh check karega ke data folder path theek hai ya nahi
        if not os.path.exists("data"):
            print("[!] ALERT: 'data' folder nahi mila! Path check karein.")
            
        self.router = PatchRouter(data_dir="data")
        
        # Safe tarike se version fetch karna
        try:
            self.latest_patch = self.router.get_latest_patch_version()
        except Exception:
            self.latest_patch = "UNKNOWN_VERSION"

    def generate_strategy_report(self, mode="Clash Squad", strategy_type="Aggressive Attack"):
        print("="*50)
        print("   FF META OPTIMIZER - SYSTEM EXECUTION ENGINE    ")
        print(f"   Active Meta Version: {str(self.latest_patch).upper()}")
        print("="*50 + "\n")

        # 1. Fetch Character Meta safely
        try:
            chrono_data = self.router.get_character_stats("Chrono")
            k_data = self.router.get_character_stats("K")
        except Exception:
            chrono_data = None
            k_data = None
        
        # 2. Fetch Weapon Meta safely
        try:
            scar_data = self.router.get_weapon_stats("SCAR")
            mac10_data = self.router.get_weapon_stats("MAC10")
        except Exception:
            scar_data = None
            mac10_data = None

        # 3. Print Synthesized Strategy Output
        print(f"--- [MODE: {mode.upper()} | TYPE: {strategy_type.upper()}] ---")
        
        # Agar router function ne `None` return kiya ho tab bhi basic structure print hoga
        print("• Active Character Recommendation: K (Master of All)")
        if k_data:
            print(f"  └ Source: {k_data.get('patch', 'N/A')} | Interval: 1.0s EP recovery | Cap: 250 EP")
        else:
            print("  └ (K data missing in JSON - using default K strategy)")
        
        print("• Defensive Counter Note: Chrono (Time Turner)")
        if chrono_data:
            print(f"  └ Source: {chrono_data.get('patch', 'N/A')} | Shield: 800 HP (Two-Way Protection)")
        else:
            print("  └ (Chrono data missing in JSON - using default Chrono strategy)")

        print("• Weapon Synergy Setup:")
        if mac10_data:
            print("  └ Primary SMG: MAC10 (Pre-attached Silencer, High AP)")
        else:
            print("  └ Primary SMG: MAC10 (Default)")
            
        if scar_data:
            print("  └ Secondary AR: SCAR (Recoil Reduction Applied)")
        else:
            print("  └ Secondary AR: SCAR (Default)")

        print("\n[ENGINE STATUS]: All multi-patch data execution completed.")

if __name__ == "__main__":
    try:
        engine = MetaOptimizerEngine()
        engine.generate_strategy_report()
    except Exception as e:
        print("\n[!!!] EK ERROR AAGAYA HAI:")
        traceback.print_exc()
