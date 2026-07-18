import numpy as np
from sklearn.neighbors import BallTree

EARTH_RADIUS = 6371.0


def extract_landing(landing_df, df):
    """
    Find the nearest landing centre for each prediction point.
    """

    landing_coords = np.deg2rad(
        landing_df[["Latitude", "Longitude"]].values
    )

    tree = BallTree(
        landing_coords,
        metric="haversine"
    )

    grid_coords = np.deg2rad(
        df[["Latitude", "Longitude"]].values
    )

    dist, ind = tree.query(
        grid_coords,
        k=1
    )

    idx = ind[:, 0]

    df["Nearest_Landing"] = (
        landing_df.iloc[idx]["Landing_Center"].values
    )

    df["Landing_State"] = (
        landing_df.iloc[idx]["State"].values
    )

    df["Landing_Distance_km"] = (
        dist[:, 0] * EARTH_RADIUS
    )

    return df