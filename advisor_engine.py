import os
import sys
import time
from interface.prompt_parser import parse_full_prompt

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.patch_router import PatchRouter
from main import HybridMetaEngine

class AdvisorEngine:
    def __init__(self):
        self.data_dir = os.path.join(current_dir, "data")
        self.router = PatchRouter(data_dir=self.data_dir)
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

        user_prompt = os.getenv("USER_PROMPT", "rush")
        if not user_prompt:
            user_prompt = "rush"
        parsed = parse_full_prompt(user_prompt)
        print(f"[*] Parsed prompt: {parsed}")

        engine = HybridMetaEngine(
            patch_name=self.active_patch_name,
            objective=parsed.get("objective", "max_damage"),
            playstyle=parsed.get("playstyle", "rush"),
            engagement_range=parsed.get("engagement_range", "mid")
        )

        max_combinations = 500000
        results = engine.run_exhaustive_search(output_limit=10, max_combinations=max_combinations)

        if not results:
            print("[-] No valid builds found.")
            return

        best_build = results[0]
        exec_time = round((time.time() - start_time) * 1000, 3)
        b = best_build["build"]
        w = best_build["weapons"]

        output_file_path = os.path.join(current_dir, "advisor_result.txt")
        response_type = parsed.get("response_type", "full_build")

        if response_type == "weapon_only":
            # Weapon-only output
            report_content = (
                f"{'=' * 70}\n"
                f"    BEST WEAPON(S) FOR YOUR QUERY\n"
                f"{'=' * 70}\n"
                f"[*] Active Patch  : {self.active_patch_name.upper()}\n"
                f"[*] Playstyle     : {engine.playstyle}\n"
                f"[*] Engagement    : {engine.engagement_range}\n"
                f"{'-' * 70}\n\n"
                f"🏆 Top Primary Weapon:\n"
                f"   • Name         : {w['primary']['name']}\n"
                f"   • TTK          : {w['primary']['ttk']}s\n"
                f"   • Effective DMG: {w['primary'].get('effective_damage', 'N/A')}\n"
                f"\n🏆 Top Secondary Weapon:\n"
                f"   • Name         : {w['secondary']['name']}\n"
                f"   • TTK          : {w['secondary']['ttk']}s\n"
                f"   • Effective DMG: {w['secondary'].get('effective_damage', 'N/A')}\n"
                f"\n💡 Recommendation: For long range, use {w['primary']['name']} as primary.\n"
                f"{'=' * 70}\n"
            )
        else:
            # Full build report
            passives_formatted = "".join([f"   • Passive {idx}        : {str(p).title()}\n" for idx, p in enumerate(b['passives'], 1)])
            report_content = (
                f"{'=' * 70}\n"
                f"    ISOLATED ADVISOR ENGINE - EXHAUSTIVE SEARCH V2\n"
                f"{'=' * 70}\n"
                f"[*] Engine Latency: {exec_time}ms\n"
                f"[*] Active Patch  : {self.active_patch_name.upper()}\n"
                f"[*] Objective     : {engine.objective}\n"
                f"[*] Playstyle     : {engine.playstyle}\n"
                f"{'-' * 70}\n\n"
                f"1. Optimal Dynamic Setup:\n"
                f"   • Active Character : {str(b['active']).title()}\n"
                f"{passives_formatted}"
                f"   • Pet Choice       : {b['pet']}\n"
                f"   • Loadout          : {b['loadout']}\n\n"
                f"2. Weapon Analysis:\n"
                f"   • Primary  : {w['primary']['name']} | TTK: {w['primary']['ttk']}s\n"
                f"   • Secondary: {w['secondary']['name']} | TTK: {w['secondary']['ttk']}s\n\n"
                f"3. Score:\n"
                f"   • Win Rate : {best_build['win_rate']}%\n"
                f"   • Raw Score: {best_build['raw_score']:.2f}\n"
                f"{'=' * 70}\n"
            )

        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            print("[+] Success! Result generated.")
            print(f"[+] Saved to: {output_file_path}\n")
            print(report_content)
        except IOError as e:
            print(f"[-] File write error: {e}")

if __name__ == "__main__":
    advisor = AdvisorEngine()
    advisor.run_isolated_advisor()
