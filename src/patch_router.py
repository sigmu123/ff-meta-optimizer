================================================
FILE: src/patch_router.py
================================================
import os
import re

class PatchRouter:
    """
    Resolves isolated patch directories and determines current active version.
    """
    def __init__(self, data_dir=None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir
            
        self.patches_dir = os.path.join(self.data_dir, "patches")

    def list_available_patches(self):
        if not os.path.exists(self.patches_dir):
            return []
        
        patches = [
            d for d in os.listdir(self.patches_dir)
            if os.path.isdir(os.path.join(self.patches_dir, d))
        ]
        return sorted(patches)

    def get_latest_patch_version(self):
        patches = self.list_available_patches()
        if not patches:
            return "patch_ob54"

        # Explicit priority search for standard release patches
        ob_patches = [p for p in patches if "ob" in p.lower()]
        if ob_patches:
            # Sort numerically by OB number extracted via regex
            def extract_ob_num(p_name):
                match = re.search(r'ob(\d+)', p_name.lower())
                return int(match.group(1)) if match else 0
            
            ob_patches.sort(key=extract_ob_num, reverse=True)
            return ob_patches[0]

        return patches[-1]
