import pandas as pd
import numpy as np
def filter_candidate_pixels(df):
    """
    Keep only candidate PFZ pixels.
    """

    before = len(df)

    df = df[
        (df["CHL"] > 0.1) &
        (df["Nearest_Front_Magnitude"].notna())
    ].copy()

    after = len(df)

    print(f"Candidate pixels: {before} -> {after}")

    return df