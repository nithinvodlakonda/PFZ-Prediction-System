"""
Shared data-prep step used by every page that loads a prediction CSV.

Per project decision: PFZ classification is only meaningful on
thermal-front candidate pixels, so every downstream view (map, table,
KPIs, analytics, trends) operates ONLY on rows where Front_Present == 1
— regardless of what else may be present in the raw CSV.
"""
import pandas as pd


def filter_front_present(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or "Front_Present" not in df.columns:
        return df
    return df[df["Front_Present"] == 1].copy()
