from datetime import date, datetime
from pathlib import Path

import numpy as np
import xarray as xr

from config import DATA_NC_PATH

_REQUIRED_FILES = ["SST.nc", "Currents.nc", "CHL.nc", "Wind.nc", "SSS.nc", "ekman.nc"]
_EPOCH = np.datetime64("1970-01-01T00:00:00")
_ONE_SECOND = np.timedelta64(1, "s")


def get_available_date_range():
    """
    Opens each required dataset from DATA_NC_PATH and returns the
    (min_date, max_date) overlap common to all datasets.
    Supports different time coordinate names such as:
    time, valid_time, forecast_time, etc.
    """
    ranges = []

    for fname in _REQUIRED_FILES:
        path = Path(DATA_NC_PATH) / fname

        with xr.open_dataset(path) as ds:
            time_var = _find_time_variable(ds)
            times = ds[time_var].values

            t_min = _to_date(times.min())
            t_max = _to_date(times.max())
            ranges.append((t_min, t_max))

    overlap_min = max(r[0] for r in ranges)
    overlap_max = min(r[1] for r in ranges)

    return overlap_min, overlap_max


def _find_time_variable(ds):
    """
    Find the dataset's time coordinate automatically.
    """

    # Common names
    for name in ["time", "valid_time", "forecast_time", "Time"]:
        if name in ds.coords or name in ds.variables:
            return name

    # Look for any datetime coordinate
    for name, coord in ds.coords.items():
        if np.issubdtype(coord.dtype, np.datetime64):
            return name

    raise KeyError(
        f"No time coordinate found in dataset. "
        f"Available coordinates: {list(ds.coords)}"
    )


def _to_date(np_datetime) -> date:
    ts = (np_datetime - _EPOCH) / _ONE_SECOND
    return datetime.utcfromtimestamp(float(ts)).date()