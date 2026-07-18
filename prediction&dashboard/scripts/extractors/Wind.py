import numpy as np
import xarray as xr

from utils import standardize_coordinates


def extract_wind(wind_ds, df):
    """
    Extract wind speed using vectorized nearest-neighbor lookup.
    """

    wind_ds = standardize_coordinates(wind_ds)

    lat = xr.DataArray(
        df["Latitude"].values,
        dims="points"
    )

    lon = xr.DataArray(
        df["Longitude"].values,
        dims="points"
    )

    u = wind_ds["u10"].sel(
        lat=lat,
        lon=lon,
        method="nearest"
    ).values

    v = wind_ds["v10"].sel(
        lat=lat,
        lon=lon,
        method="nearest"
    ).values

    df["WIND_SPEED"] = np.sqrt(
        np.squeeze(u) ** 2 +
        np.squeeze(v) ** 2
    )

    return df