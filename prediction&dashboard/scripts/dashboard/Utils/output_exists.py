"""
REFERENCE IMPLEMENTATION — matches the documented contract exactly.
Your existing production Utils/output_exists.py already does this; this
file exists only so the dashboard can be run and demoed standalone.
"""
from datetime import date
from pathlib import Path


def output_exists(output_path: str, selected_date: date) -> bool:
    date_str = selected_date.strftime("%Y-%m-%d")
    folder = Path(output_path) / date_str
    required = [
        folder / f"pfz_prediction_{date_str}.csv",
        folder / f"PFZ_Output_{date_str}.png",
        folder / f"PFZ_Output_{date_str}.nc",
    ]
    return all(p.exists() for p in required)
