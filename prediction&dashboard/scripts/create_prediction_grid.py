import pandas as pd
import numpy as np


def create_prediction_grid(sst_ds, selected_date):
    """
    Create the prediction grid from the SST dataset.

    Parameters
    ----------
    sst_ds : xarray.Dataset
        SST dataset for the selected date.
    selected_date : datetime/date/str
        Date selected by the user.

    Returns
    -------
    pandas.DataFrame
    """

    # Standardize coordinate names
    if "latitude" in sst_ds.coords:
        sst_ds = sst_ds.rename({
            "latitude": "lat",
            "longitude": "lon"
        })

    # Convert selected date
    date = pd.to_datetime(selected_date)

    # Create prediction grid
    lat = sst_ds["lat"].values
    lon = sst_ds["lon"].values

    lon_grid, lat_grid = np.meshgrid(lon, lat)

    df = pd.DataFrame({
        "Date": date,
        "Latitude": lat_grid.ravel(),
        "Longitude": lon_grid.ravel()
    })

    return df