import numpy as np
import xarray as xr

from utils import standardize_coordinates


def extract_current(current_ds, df):
    """
    Extract SSH and current speed using vectorized nearest-neighbor lookup.
    """

    current_ds = standardize_coordinates(current_ds)

    lat = xr.DataArray(
        df["Latitude"].values,
        dims="points"
    )

    lon = xr.DataArray(
        df["Longitude"].values,
        dims="points"
    )

    ssh = current_ds["sla"].sel(
        lat=lat,
        lon=lon,
        method="nearest"
    ).values

    u = current_ds["ugos"].sel(
        lat=lat,
        lon=lon,
        method="nearest"
    ).values

    v = current_ds["vgos"].sel(
        lat=lat,
        lon=lon,
        method="nearest"
    ).values

    df["SSH"] = np.squeeze(ssh)

    df["curr_Speed"] = np.sqrt(
        np.squeeze(u) ** 2 +
        np.squeeze(v) ** 2
    )

    return df