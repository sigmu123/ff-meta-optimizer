import sys
from core.ttk_calculator import MechanicsEngine

def main():
    print("==========================================================")
    print("      FREE FIRE QUANTITATIVE META ENGINE (v1.0.0)         ")
    print("==========================================================")
    print("[SYSTEM LOG]: Loading Engine Modules...")
    print("[SYSTEM LOG]: Testing Core Mechanics Engine...")
    
    # Test Damage Calculation (Sample: Base Dmg 30, Range Decay 0%, Vest L2 50%, Armor Pen 0%)
    sample_dmg = MechanicsEngine.calculate_effective_damage(30, 0.0, 0.50, 0.0)
    sample_ttk = MechanicsEngine.calculate_ttk(200, sample_dmg, 100)
    
    print(f"[TEST RESULT]: Sample Effective Dmg: {sample_dmg} | BTK: {sample_ttk['btk']} | TTK: {sample_ttk['ttk_sec']}s")
    print("[SYSTEM LOG]: Engine Initialized. Ready for Patch Data Schemas.")
    print("==========================================================\n")

if __name__ == "__main__":
    main()
