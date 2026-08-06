import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

class PatchRouter:
    """
    Dynamic Multi-Directory Patch Router for Free Fire Meta Engine.
    Handles legacy single-file structures as well as recursive subdirectory schemas.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir) / "patches" if (Path(data_dir) / "patches").exists() else Path(data_dir)
        self.patches: Dict[str, Dict[str, Any]] = {}
        self.load_all_patches()

    def _read_json(self, file_path: Path) -> Dict[str, Any]:
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def load_all_patches(self):
        """Dynamically scans data/patches/ and loads patch content recursively."""
        if not self.data_dir.exists():
            return
        
        patch_folders = sorted([d for d in self.data_dir.iterdir() if d.is_dir()])
        for folder in patch_folders:
            patch_name = folder.name
            patch_content = {
                "characters": [],
                "weapons": [],
                "mechanics": {},
                "pets_loadout": {}
            }

            # Walk through all JSON files in subdirectories
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(".json") and file != "patch_manifest.json":
                        full_path = Path(root) / file
                        data = self._read_json(full_path)
                        
                        # Category mapping logic
                        if "character" in file or "skill" in file:
                            if isinstance(data, list):
                                patch_content["characters"].extend(data)
                            elif isinstance(data, dict):
                                updates = data.get("updates", data.get("active_skills", data.get("passive_skills", [])))
                                if isinstance(updates, list):
                                    patch_content["characters"].extend(updates)
                                else:
                                    patch_content["characters"].append(data)
                        
                        elif "weapon" in file or "attribute" in file or "decay" in file:
                            if isinstance(data, list):
                                patch_content["weapons"].extend(data)
                            elif isinstance(data, dict):
                                w_list = data.get("weapons", data.get("weapon_adjustments", data.get("new_weapons", [])))
                                if isinstance(w_list, list):
                                    patch_content["weapons"].extend(w_list)
                                else:
                                    patch_content["weapons"].append(data)

                        elif "pets" in file or "loadout" in file:
                            patch_content["pets_loadout"][file] = data

                        else:
                            patch_content["mechanics"][file] = data

            self.patches[patch_name] = patch_content

    def get_latest_patch_version(self) -> Optional[str]:
        """Returns the highest active patch directory key."""
        if not self.patches:
            return None
        # Prefer explicit active patch if flagged, otherwise return last in sorted order
        for p_name, p_data in self.patches.items():
            manifest = p_data.get("mechanics", {}).get("patch_manifest.json", {})
            if manifest.get("is_active"):
                return p_name
        return sorted(list(self.patches.keys()))[-1]

    def get_character_stats(self, char_name: str, patch_version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetches character data with automatic fallback trace across patches."""
        target_patch = patch_version or self.get_latest_patch_version()
        patch_keys = sorted(list(self.patches.keys()), reverse=True)

        if target_patch in patch_keys:
            idx = patch_keys.index(target_patch)
            patch_keys = patch_keys[idx:]

        for p_key in patch_keys:
            chars = self.patches[p_key].get("characters", [])
            for c in chars:
                c_name = c.get("character_name", c.get("name", c.get("character_id", "")))
                if str(c_name).lower() == char_name.lower():
                    return {"patch": p_key, "data": c}
        return None

    def get_weapon_stats(self, weapon_name: str, patch_version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetches weapon data with automatic fallback trace."""
        target_patch = patch_version or self.get_latest_patch_version()
        patch_keys = sorted(list(self.patches.keys()), reverse=True)

        if target_patch in patch_keys:
            idx = patch_keys.index(target_patch)
            patch_keys = patch_keys[idx:]

        for p_key in patch_keys:
            weaps = self.patches[p_key].get("weapons", [])
            for w in weaps:
                w_name = w.get("weapon_name", w.get("name", w.get("weapon_id", "")))
                if str(w_name).lower() == weapon_name.lower():
                    return {"patch": p_key, "data": w}
        return None


if __name__ == "__main__":
    router = PatchRouter()
    print(f"[ROUTER TEST] Loaded Patches: {list(router.patches.keys())}")
    print(f"[ROUTER TEST] Latest Patch: {router.get_latest_patch_version()}")
    print(f"[ROUTER TEST] Fetching Kenta: {router.get_character_stats('kenta')}")
