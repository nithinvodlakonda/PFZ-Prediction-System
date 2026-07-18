"""
REFERENCE IMPLEMENTATION — matches the documented contract exactly.
Your existing production Utils/output_loader.py already does this; this
file exists only so the dashboard can be run and demoed standalone.
"""
from datetime import date
from pathlib import Path

import pandas as pd


def load_outputs(output_folder: str, selected_date: date) -> dict:
    date_str = selected_date.strftime("%Y-%m-%d")
    folder = Path(output_folder) / date_str

    csv_path = folder / f"pfz_prediction_{date_str}.csv"
    png_path = folder / f"PFZ_Output_{date_str}.png"
    nc_path = folder / f"PFZ_Output_{date_str}.nc"

    result = {
        "csv": str(csv_path) if csv_path.exists() else None,
        "png": str(png_path) if png_path.exists() else None,
        "nc": str(nc_path) if nc_path.exists() else None,
        "df": None,
    }
    if result["csv"]:
        result["df"] = pd.read_csv(result["csv"])
    return result
