import numpy as np


def standardize_coordinates(ds):
    """
    Standardize latitude and longitude names.
    """

    rename_dict = {}

    if "latitude" in ds:
        rename_dict["latitude"] = "lat"

    if "longitude" in ds:
        rename_dict["longitude"] = "lon"

    if rename_dict:
        ds = ds.rename(rename_dict)

    return ds


import xarray as xr


def extract_variable(ds, variable, df, column_name):
    """
    Extract a variable from a NetCDF dataset using vectorized nearest neighbour.
    """

    ds = standardize_coordinates(ds)

    lat = xr.DataArray(
        df["Latitude"].values,
        dims="points"
    )

    lon = xr.DataArray(
        df["Longitude"].values,
        dims="points"
    )

    values = ds[variable].sel(
        lat=lat,
        lon=lon,
        method="nearest"
    ).values

    df[column_name] = values.squeeze()

    return df