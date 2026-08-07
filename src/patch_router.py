import os

class PatchRouter:
    def __init__(self, data_dir="data"):
        self.patches_dir = os.path.join(data_dir, "patches")

    def get_all_patch_versions(self):
        if not os.path.exists(self.patches_dir):
            return []
        patches = [
            d for d in os.listdir(self.patches_dir)
            if os.path.isdir(os.path.join(self.patches_dir, d))
        ]
        return sorted(patches)

    def get_latest_patch_version(self):
        patches = self.get_all_patch_versions()
        if "patch_ob54" in patches:
            return "patch_ob54"
        if patches:
            return sorted(patches)[-1]
        return "patch_ob54"
