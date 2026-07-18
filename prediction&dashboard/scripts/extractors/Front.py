import numpy as np
from sklearn.neighbors import BallTree

from utils import standardize_coordinates


def extract_front(front_ds, df):
    """
    Extract nearest front magnitude and front presence.
    """

    front_ds = standardize_coordinates(front_ds)

    # -------------------------
    # Front Magnitude (nearest front)
    # -------------------------
    mask = front_ds["front_present"].values == 1

    if not np.any(mask):
        df["Nearest_Front_Magnitude"] = np.nan
        df["Front_Present"] = 0
        return df

    rows, cols = np.where(mask)

    front_lat = front_ds["lat"].values[rows]
    front_lon = front_ds["lon"].values[cols]
    front_mag = front_ds["front_magnitude"].values[rows, cols]

    valid = (
        ~np.isnan(front_lat)
        & ~np.isnan(front_lon)
        & ~np.isnan(front_mag)
    )

    front_lat = front_lat[valid]
    front_lon = front_lon[valid]
    front_mag = front_mag[valid]

    tree = BallTree(
        np.deg2rad(np.column_stack((front_lat, front_lon))),
        metric="haversine",
    )

    coords = np.deg2rad(df[["Latitude", "Longitude"]].values)

    _, ind = tree.query(coords, k=1)

    df["Nearest_Front_Magnitude"] = front_mag[ind[:, 0]]

    # -------------------------
    lat = front_ds["lat"].values
    lon = front_ds["lon"].values

# Find nearest latitude index for each point
    lat_idx = np.abs(lat[:, None] - df["Latitude"].values).argmin(axis=0)

# Find nearest longitude index for each point
    lon_idx = np.abs(lon[:, None] - df["Longitude"].values).argmin(axis=0)

# Extract front_present values
    df["Front_Present"] = front_ds["front_present"].values[
        lat_idx,
        lon_idx
        ].astype(np.int8)
    return df