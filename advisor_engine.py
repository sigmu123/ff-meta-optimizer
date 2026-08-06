import os
import sys
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.append(current_dir)

from main import QuickExecutionEngine

class AdvisorEngine:
    def __init__(self, loader=None):
        self.engine = QuickExecutionEngine()

    def display_patch_summary(self):
        """Runs the Master Execution Pipeline and prints Quick Execution Sheet."""
        self.engine.generate_quick_execution_sheet(user_prompt="meta rush build")

if __name__ == "__main__":
    try:
        advisor = AdvisorEngine()
        advisor.display_patch_summary()
    except Exception:
        print("\n[!] Critical Failure in AdvisorEngine:")
        traceback.print_exc()
