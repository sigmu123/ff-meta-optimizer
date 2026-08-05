import os
import json
from pathlib import Path

class PatchRouter:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.patches = {}
        self.load_all_patches()

    def load_all_patches(self):
        """Dynamically scans data/ and loads all patch folders in sorted order."""
        if not self.data_dir.exists():
            return
        
        patch_folders = sorted([d for d in self.data_dir.iterdir() if d.is_dir() and d.name.startswith("patch_")])
        for folder in patch_folders:
            patch_name = folder.name
            self.patches[patch_name] = {
                "characters": self._read_json(folder / "characters.json"),
                "weapons": self._read_json(folder / "weapons.json"),
                "modes_and_maps": self._read_json(folder / "modes_and_maps.json"),
                "system_qol": self._read_json(folder / "system_qol.json")
            }

    def _read_json(self, file_path):
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_latest_patch_version(self):
        """Returns the highest active patch key (e.g., 'patch_v2')."""
        if not self.patches:
            return None
        return sorted(list(self.patches.keys()))[-1]

    def get_character_stats(self, char_name, patch_version=None):
        """Fetches character data with automatic fallback to previous patches if missing."""
        target_patch = patch_version or self.get_latest_patch_version()
        patch_keys = sorted(list(self.patches.keys()), reverse=True)
        
        if target_patch in patch_keys:
            # Reorder starting from target patch downwards
            idx = patch_keys.index(target_patch)
            patch_keys = patch_keys[idx:]

        for p_key in patch_keys:
            chars = self.patches[p_key].get("characters", {}).get("character_adjustments", [])
            for c in chars:
                if c.get("name").lower() == char_name.lower():
                    return {"patch": p_key, "data": c}
        return None

    def get_weapon_stats(self, weapon_name, patch_version=None):
        """Fetches weapon data with automatic fallback trace."""
        target_patch = patch_version or self.get_latest_patch_version()
        patch_keys = sorted(list(self.patches.keys()), reverse=True)

        if target_patch in patch_keys:
            idx = patch_keys.index(target_patch)
            patch_keys = patch_keys[idx:]

        for p_key in patch_keys:
            weaps = self.patches[p_key].get("weapons", {}).get("weapon_adjustments", [])
            for w in weaps:
                if w.get("name").lower() == weapon_name.lower():
                    return {"patch": p_key, "data": w}
        return None

if __name__ == "__main__":
    router = PatchRouter()
    print(f"Active Router Loaded Patches: {list(router.patches.keys())}")
    print(f"Latest Active Meta: {router.get_latest_patch_version()}")
