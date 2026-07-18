import xarray as xr
import numpy as np
from config import OUTPUT_PATH
import os

def PFZ_file(df, sst_ds):
    """
    Create final PFZ NetCDF file.

    Parameters
    ----------
    df : pandas.DataFrame
        Final prediction dataframe.

    sst_ds : xarray.Dataset
        SST dataset containing analysed_sst.

    output_file : str
        Output NetCDF filename.
    """

    # -----------------------------
    # Extract SST
    # -----------------------------
    sst = sst_ds["analysed_sst"].values

    # -----------------------------
    # Encode PFZ
    # -----------------------------
    pfz_map = {
        "Low": 0,
        "Medium": 1,
        "High": 2
    }

    df = df.copy()
    df["PFZ_Code"] = df["PFZ"].map(pfz_map)

    # -----------------------------
    # Coordinates
    # -----------------------------
    lat = np.sort(df["Latitude"].unique())
    lon = np.sort(df["Longitude"].unique())

    # -----------------------------
    # Create 2D grids
    # -----------------------------
    pfz_grid = (
        df.pivot(
            index="Latitude",
            columns="Longitude",
            values="PFZ_Code"
        )
        .sort_index()
        .values
    )

    front_grid = (
        df.pivot(
            index="Latitude",
            columns="Longitude",
            values="Front_Present"
        )
        .sort_index()
        .values
    )

    confidence_grid = (
        df.pivot(
            index="Latitude",
            columns="Longitude",
            values="Confidence"
        )
        .sort_index()
        .values
    )

    # -----------------------------
    # Create Dataset
    # -----------------------------
    ds = xr.Dataset(

        data_vars={

            "SST": (
                ("latitude", "longitude"),
                sst
            ),

            "PFZ": (
                ("latitude", "longitude"),
                pfz_grid
            ),

            "Front_Present": (
                ("latitude", "longitude"),
                front_grid
            ),

            "Confidence": (
                ("latitude", "longitude"),
                confidence_grid
            ),
        },

        coords={

            "latitude": lat,
            "longitude": lon

        }

    )

    # -----------------------------
    # Variable Attributes
    # -----------------------------
    ds["SST"].attrs = {
        "units": "degree_Celsius",
        "long_name": "Sea Surface Temperature"
    }

    ds["PFZ"].attrs = {
        "long_name": "Potential Fishing Zone",
        "flag_values": np.array([0, 1, 2], dtype=np.int8),
        "flag_meanings": "Low Medium High"
    }

    ds["Front_Present"].attrs = {
        "long_name": "Thermal Front Presence",
        "flag_values": np.array([0, 1], dtype=np.int8),
        "flag_meanings": "No Yes"
    }

    ds["Confidence"].attrs = {
        "long_name": "Prediction Confidence"
    }

    # -----------------------------
    # Global Attributes
    # -----------------------------
    ds.attrs = {
        "title": "Potential Fishing Zone Prediction",
        "source": "Machine Learning Pipeline",
        "institution": "INCOIS",
    }


    return ds