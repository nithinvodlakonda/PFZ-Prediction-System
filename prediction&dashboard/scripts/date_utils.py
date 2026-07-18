import os
import xarray as xr
import pandas as pd

from config import DATA_NC_PATH


def get_available_date_range():
    """
    Find the common available date range across all gridded datasets.
    """

    files = [
        "SST.nc",
        "Currents.nc",
        "CHL.nc",
        "Wind.nc",
        "SSS.nc",
        "ekman.nc"
    ]

    start_dates = []
    end_dates = []

    for file in files:

        path = os.path.join(DATA_NC_PATH, file)

        ds = xr.open_dataset(path)

        # Find time coordinate
        if "time" in ds.coords:
            time = pd.to_datetime(ds["time"].values)

        elif "valid_time" in ds.coords:
            time = pd.to_datetime(ds["valid_time"].values)

        else:
            ds.close()
            continue

        start_dates.append(time.min())
        end_dates.append(time.max())

        ds.close()

    # Common overlapping period
    min_date = max(start_dates)
    max_date = min(end_dates)

    return min_date.date(), max_date.date()