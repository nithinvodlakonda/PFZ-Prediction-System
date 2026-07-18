import os
import re
from config import DATA_NC_PATH, DATA_PATH
import pandas as pd


def validate_files(selected_date):

    files = {
        "SST": os.path.join(DATA_NC_PATH, "SST.nc"),
        "CURRENT": os.path.join(DATA_NC_PATH, "Currents.nc"),
        "CHL": os.path.join(DATA_NC_PATH, "CHL.nc"),
        "WIND": os.path.join(DATA_NC_PATH,"Wind.nc"),
        "SSS": os.path.join(DATA_NC_PATH, "SSS.nc"),
        "CYCLONIC": os.path.join(DATA_NC_PATH,"cyclonic.nc"),
        "ANTICYCLONIC": os.path.join(DATA_NC_PATH, "anticyclonic.nc"),
        "DEPTH": os.path.join(DATA_PATH, "DEPTH.nc"),
        "COAST": os.path.join(DATA_PATH, "ne_10m_coastline.shp"),
        "EKMAN": os.path.join(DATA_NC_PATH, "ekman.nc"),
    }

    for name, path in files.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"{name} file not found: {path}")

    return {
        "date": pd.to_datetime(selected_date),
        "files": files
    }

if __name__ == "__main__":
    validate_files()