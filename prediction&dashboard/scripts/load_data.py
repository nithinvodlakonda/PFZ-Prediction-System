import os
import xarray as xr
import pandas as pd
import geopandas as gpd

from config import DATA_PATH, DATA_NC_PATH


def load_input_dataset(dataset_name):
    """
    Load an environmental dataset from the Data_nc folder.
    """

    file_map = {
        "SST": "SST.nc",
        "CURRENT": "Currents.nc",
        "CHL": "CHL.nc",
        "WIND": "Wind.nc",
        "SSS": "SSS.nc",
        "CYCLONIC": "cyclonic.nc",
        "ANTICYCLONIC": "anticyclonic.nc",
        "EKMAN": "ekman.nc",
    }

    if dataset_name not in file_map:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    path = os.path.join(DATA_NC_PATH, file_map[dataset_name])

    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found.")

    print(f"Loading {dataset_name}...")

    return xr.open_dataset(path)


def load_static_data(file_name):
    """
    Load static datasets from the Data folder.
    """

    path = os.path.join(DATA_PATH, file_name)

    if not os.path.exists(path):
        raise FileNotFoundError(f"{file_name} not found.")

    if file_name.endswith(".nc"):
        return xr.open_dataset(path)

    elif file_name.endswith(".csv"):
        return pd.read_csv(path)

    elif file_name.endswith(".shp"):
        return gpd.read_file(path)

    else:
        raise ValueError(f"Unsupported file type: {file_name}")


def load_all_datasets():
    """
    Load all datasets required for prediction.
    """

    datasets = {
        "SST": load_input_dataset("SST"),
        "CURRENT": load_input_dataset("CURRENT"),
        "CHL": load_input_dataset("CHL"),
        "WIND": load_input_dataset("WIND"),
        "SSS": load_input_dataset("SSS"),
        "CYCLONIC": load_input_dataset("CYCLONIC"),
        "ANTICYCLONIC": load_input_dataset("ANTICYCLONIC"),

        # Static datasets
        "DEPTH": load_static_data("DEPTH.nc"),
        "COAST": load_static_data("ne_10m_coastline.shp"),
        "EKMAN": load_input_dataset("EKMAN"),
    }

    return datasets
    
def standardize_dataset(ds):

    rename_dict = {}

    if "valid_time" in ds.coords:
        rename_dict["valid_time"] = "time"

    if "latitude" in ds.coords:
        rename_dict["latitude"] = "lat"

    if "longitude" in ds.coords:
        rename_dict["longitude"] = "lon"

    if rename_dict:
        ds = ds.rename(rename_dict)

    return ds

if __name__ == "__main__":
    datasets = load_all_datasets()
    print("Loaded datasets:")
    print(list(datasets.keys()))