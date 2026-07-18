import numpy as np
import xarray as xr

from utils import standardize_coordinates


def extract_depth(depth_ds, df):
    """
    Extract bathymetry (depth) for every prediction point
    and remove land points.
    """

    depth_ds = standardize_coordinates(depth_ds)

    lat = xr.DataArray(
        df["Latitude"].values,
        dims="points"
    )

    lon = xr.DataArray(
        df["Longitude"].values,
        dims="points"
    )

    depth = depth_ds["elevation"].sel(
        lat=lat,
        lon=lon,
        method="nearest"
    ).values

    depth = np.squeeze(depth)

    # Store depth
    df["Depth"] = np.abs(depth)

    # Remove land (assuming elevation == 0)
    df = df[depth != 0].reset_index(drop=True)

    return df