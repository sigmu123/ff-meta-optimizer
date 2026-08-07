================================================
FILE: src/patch_ingestor.py
================================================
import os
import json

class PatchIngestor:
    """
    Validates and ingests raw JSON definitions into memory structures.
    """
    @staticmethod
    def validate_and_load(json_path: str) -> dict:
        if not os.path.exists(json_path):
            return {}
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
