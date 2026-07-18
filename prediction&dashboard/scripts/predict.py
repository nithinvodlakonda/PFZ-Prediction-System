import joblib
import pandas as pd

from config import MODEL_PATH

model = joblib.load(
    f"{MODEL_PATH}/extra_trees_pfz_model.pkl"
)

label_encoder = joblib.load(
    f"{MODEL_PATH}/label_encoder.pkl"
)

FEATURES = [
   'SST',
    'curr_Speed',
    'SSH',
    'Nearest_Front_Magnitude',
    'Depth',
    'SSS',
    'log_chl',
    'SST_X_CHL',
    'Month_sin',
    'Month_cos',
    'DOY_sin',
    'DOY_cos',
    'Distance_to_Coast_km',"WIND_SPEED",
    'Nearest_Eddy_Distance_km','Inside_Eddy', 'Ekman_X', 'Ekman_Y'
]

def predict(df):

    X = df[FEATURES]

    pred = model.predict(X)

    prob = model.predict_proba(X)

    df["PFZ"] = label_encoder.inverse_transform(pred)

    df["Confidence"] = prob.max(axis=1)
    # Rename prediction column
    # =====================================================
    # Standardize Dashboard Column Names
    # =====================================================

    # -------------------------------------------------------
    # Dashboard Friendly Columns
    # -------------------------------------------------------

    df["Catch_Category"] = df["PFZ"]

    df = df.rename(columns={

        "WIND_SPEED": "Wind_Speed",

        "curr_Speed": "Current_Speed",

        "Nearest_Front_Magnitude": "Front_Magnitude",

    })

    return df