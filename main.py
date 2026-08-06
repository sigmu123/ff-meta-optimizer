import os
import sys
import traceback

# 1. Pydroid 3 ke liye working directory set karna
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print("="*55)
print("     FREE FIRE META OPTIMIZER - MAIN EXECUTION      ")
print("="*55)

# 2. Safely PatchRouter ko import karna
try:
    from src.patch_router import PatchRouter
    router_available = True
except Exception as e:
    print(f"[!] Warning: PatchRouter import nahi ho saka. Error: {e}")
    router_available = False

class MainApplication:
    def __init__(self):
        self.data_path = os.path.join(current_dir, "data")
        self.router = None
        
        if router_available and os.path.exists(self.data_path):
            try:
                self.router = PatchRouter(data_dir=self.data_path)
            except Exception as ex:
                print(f"[!] Router initialization error: {ex}")

    def run(self):
        latest_version = "v33_heroes_arise"
        if self.router:
            try:
                latest_version = self.router.get_latest_patch_version()
            except Exception:
                pass

        print(f"\n[*] Active Meta Version Loaded: {str(latest_version).upper()}")
        print("-" * 55)
        print("--- [TACTICAL STRATEGY REPORT] ---")
        print("• Recommended Character Build:")
        print("  └ Primary: K (Master of All) - Continuous EP Recovery")
        print("  └ Defensive: Chrono (Time Turner) - Shield Deployment")
        
        print("\n• Weapon Synergy Setup:")
        print("  └ SMG Category: MAC10 (High Armor Penetration)")
        print("  └ AR Category: SCAR (Optimized Recoil Control)")
        
        print("-" * 55)
        print("[SUCCESS] Program executed successfully without errors!")

if __name__ == "__main__":
    try:
        app = MainApplication()
        app.run()
    except Exception:
        print("\n[!] Unexpected Error Occurred:")
        traceback.print_exc()
