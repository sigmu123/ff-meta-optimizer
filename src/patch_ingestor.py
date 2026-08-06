import os
import json
from pathlib import Path

class PatchIngestor:
    """
    Validates and ingests historical and new patch data into ff-meta-optimizer directory schema.
    """
    def __init__(self, patches_dir="data/patches"):
        self.patches_dir = Path(patches_dir)

    def scan_and_validate(self):
        print("=" * 60)
        print("         FREE FIRE PATCH INGESTION & VALIDATION LOG          ")
        print("=" * 60)

        if not self.patches_dir.exists():
            print(f"[!] Error: Path {self.patches_dir} does not exist.")
            return

        patch_folders = sorted([d for d in self.patches_dir.iterdir() if d.is_dir()])
        print(f"[*] Total Patch Folders Detected: {len(patch_folders)}\n")

        for folder in patch_folders:
            manifest_file = folder / "patch_manifest.json"
            has_manifest = manifest_file.exists()
            
            # Count total json files inside patch
            json_files = list(folder.glob("**/*.json"))
            
            status = "VALID" if has_manifest else "WARNING (Missing Manifest)"
            print(f" -> [{status}] {folder.name} | JSON Files: {len(json_files)}")

        print("-" * 60)
        print("[SUCCESS] All ingested patches scanned successfully!")
        print("=" * 60)

if __name__ == "__main__":
    ingestor = PatchIngestor()
    ingestor.scan_and_validate()
