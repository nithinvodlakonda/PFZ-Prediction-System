"""
Analytics — tightened from the old four-tab sprawl. Uses the confirmed
real schema directly (no defensive `if col in df.columns` guessing).

Operates on Front_Present == 1 pixels only (per project decision) and
includes a Model Feature Importance section (the "ML block"), read from
a feature_importance.csv the model training step saves under MODEL_PATH.
"""
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(CURRENT_DIR)
SCRIPTS_DIR = os.path.dirname(DASHBOARD_DIR)

for path in [CURRENT_DIR, DASHBOARD_DIR, SCRIPTS_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)
from config import OUTPUT_PATH, MODEL_PATH
from Utils.archive import get_prediction_archive
from Utils.output_loader import load_outputs

from components.theme import header_bar
from components.charts import category_distribution_bar, parameter_histogram, feature_importance_bar
from components.data_prep import filter_front_present
from components.colors import TEAL, NAVY

header_bar("Analytics", "Distribution, parameter, and model analysis for a single prediction run.")

archive = get_prediction_archive(OUTPUT_PATH)
if not archive:
    st.info("No archived prediction runs yet — generate at least one on the Classifier page.")
    st.stop()

archive_dates = [a["Date"] for a in archive]  # already reverse-chronological
selected_date_str = st.selectbox("Prediction date", archive_dates)
selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

outputs = load_outputs(OUTPUT_PATH, selected_date)
raw_df = outputs.get("df")

if raw_df is None or raw_df.empty:
    st.warning("Could not load the prediction file for this date.")
    st.stop()

df = filter_front_present(raw_df)
st.caption(
    f"Analyzing {len(df):,} thermal-front candidate pixels "
    f"(Front_Present == 1) out of {len(raw_df):,} total grid pixels."
)

st.markdown(f"#### PFZ Category Breakdown — {selected_date_str}")
st.plotly_chart(category_distribution_bar(df, "PFZ"), use_container_width=True)

st.divider()
st.markdown("#### Ocean Parameter Distributions")

param_rows = [
    ("SST", "Sea Surface Temperature"),
    ("CHL", "Chlorophyll-a"),
    ("SSH", "Sea Surface Height"),
    ("Wind_Speed", "Wind Speed"),
    ("SSS", "Sea Surface Salinity"),
    ("Current_Speed", "Current Speed"),
    ("Depth", "Bathymetry (Depth)"),
    ("Distance_to_Coast_km", "Distance to Coast (km)"),
]

colors = [NAVY, TEAL]
for i in range(0, len(param_rows), 2):
    cols = st.columns(2)
    for j, (col_name, title) in enumerate(param_rows[i:i + 2]):
        with cols[j]:
            st.plotly_chart(
                parameter_histogram(df, col_name, title=title, color=colors[j % 2]),
                use_container_width=True,
            )

st.divider()
st.markdown("#### Summary Statistics")
summary_cols = [c for c, _ in param_rows]
st.dataframe(df[summary_cols].describe().T, use_container_width=True)

st.divider()
st.markdown("#### Model — Feature Importance")
fi_path = Path(MODEL_PATH) / "feature_importance.csv"
if fi_path.exists():
    fi_df = pd.read_csv(fi_path)
    # Tolerate either exact ("Feature","Importance") or lowercase headers
    cols_lower = {c.lower(): c for c in fi_df.columns}
    feature_col = cols_lower.get("feature", fi_df.columns[0])
    importance_col = cols_lower.get("importance", fi_df.columns[1])
    st.plotly_chart(
        feature_importance_bar(fi_df, feature_col, importance_col),
        use_container_width=True,
    )
else:
    st.info(
        f"No feature_importance.csv found at {fi_path}. "
        "Save the Extra Trees Classifier's feature importances there to show this chart."
    )
