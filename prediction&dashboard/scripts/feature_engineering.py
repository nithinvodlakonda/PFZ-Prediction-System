import numpy as np


def feature_engineering(df):
    """
    Create engineered features required by the trained model.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    # ----------------------------
    # Log CHL
    # ----------------------------
    df["log_chl"] = np.log1p(df["CHL"])

    # ----------------------------
    # SST × CHL
    # ----------------------------
    df["SST_X_CHL"] = df["SST"] * df["log_chl"]

    # ----------------------------
    # Wind × Current
    # ----------------------------
    df["wind_X_curr"] = (
        df["WIND_SPEED"] *
        df["curr_Speed"]
    )

    # ----------------------------
    # Date Features
    # ----------------------------
    df["Date"] = df["Date"].astype("datetime64[ns]")

    df["Month"] = df["Date"].dt.month

    df["DOY"] = df["Date"].dt.dayofyear

    # ----------------------------
    # Month Cyclic Encoding
    # ----------------------------
    df["Month_sin"] = np.sin(
        2 * np.pi * df["Month"] / 12
    )

    df["Month_cos"] = np.cos(
        2 * np.pi * df["Month"] / 12
    )

    # ----------------------------
    # DOY Cyclic Encoding
    # ----------------------------
    df["DOY_sin"] = np.sin(
        2 * np.pi * df["DOY"] / 365
    )

    df["DOY_cos"] = np.cos(
        2 * np.pi * df["DOY"] / 365
    )

    # Remove temporary columns
    df.drop(
        columns=["Month", "DOY"],
        inplace=True
    )

    return df