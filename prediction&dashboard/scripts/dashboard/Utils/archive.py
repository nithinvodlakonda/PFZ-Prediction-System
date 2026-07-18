"""
REFERENCE IMPLEMENTATION — matches the documented contract exactly.
Your existing production Utils/archive.py already does this (it was
present but unused in the old build); this file exists only so the
dashboard can be run and demoed standalone.
"""
from pathlib import Path


def get_prediction_archive(output_path: str) -> list[dict]:
    root = Path(output_path)
    if not root.exists():
        return []

    entries = []
    for sub in root.iterdir():
        if sub.is_dir():
            entries.append({"Date": sub.name, "Folder": str(sub)})

    entries.sort(key=lambda e: e["Date"], reverse=True)
    return entries
