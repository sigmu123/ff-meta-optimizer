import os

class PatchRouter:
    def __init__(self, data_dir=None):
        if not data_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
        self.patches_dir = os.path.join(data_dir, "patches")

    def get_latest_patch_version(self):
        if not os.path.exists(self.patches_dir):
            return "patch_ob54"
            
        folders = [f for f in os.listdir(self.patches_dir) if os.path.isdir(os.path.join(self.patches_dir, f)) and f.startswith("patch_")]
        if not folders:
            return "patch_ob54"
            
        # Preference to OB versions sorted numerically
        ob_patches = sorted([f for f in folders if "ob" in f], key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))
        if ob_patches:
            return ob_patches[-1]
            
        return sorted(folders)[-1]
