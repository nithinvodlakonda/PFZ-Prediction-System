"""
Point Inspector — shows full per-pixel detail for whatever point is
currently selected on the map. This is the only place eddy fields and
Confidence are surfaced, per the schema notes (never in the main table).
"""
import pandas as pd
import streamlit as st

from components.colors import CATEGORY_COLORS

# Engineered / ML-only columns must never be shown in the UI, even here.
_HIDDEN_COLS = {
    "log_chl", "SST_X_CHL", "wind_X_curr",
    "Month_sin", "Month_cos", "DOY_sin", "DOY_cos",
}

_FIELD_LABELS = {
    "Date": "Date",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "CHL": "Chlorophyll-a (CHL)",
    "Front_Magnitude": "Front Magnitude",
    "Front_Present": "Front Present",
    "Depth": "Depth (Bathymetry)",
    "SSH": "Sea Surface Height",
    "Current_Speed": "Current Speed",
    "Wind_Speed": "Wind Speed",
    "SSS": "Sea Surface Salinity",
    "Ekman_X": "Ekman Transport (X)",
    "Ekman_Y": "Ekman Transport (Y)",
    "SST": "Sea Surface Temperature",
    "Distance_to_Coast_km": "Distance to Coast (km)",
    "Inside_Eddy": "Inside Eddy",
    "Nearest_Eddy_Distance_km": "Nearest Eddy Distance (km)",
    "Nearest_Eddy_Type": "Nearest Eddy Type",
    "PFZ": "PFZ Classification",
}


def render_point_inspector(row: pd.Series | None):
    st.markdown("#### Point Inspector")

    if row is None:
        st.caption("Click a point on the map above to inspect its full oceanographic profile.")
        return

    category = row.get("PFZ", None)
    color = CATEGORY_COLORS.get(category, "#5B6472")

    if category:
        st.markdown(
            f'<span class="pfz-pill" style="background-color:{color};">{category}</span>',
            unsafe_allow_html=True,
        )

    cols = st.columns(3)
    i = 0
    for field, label in _FIELD_LABELS.items():
        if field in _HIDDEN_COLS or field not in row.index:
            continue
        value = row[field]
        if isinstance(value, float):
            value = f"{value:.3f}"
        with cols[i % 3]:
            st.metric(label, value)
        i += 1
