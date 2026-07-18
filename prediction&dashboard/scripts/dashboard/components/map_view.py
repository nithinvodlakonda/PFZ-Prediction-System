"""
Interactive PFZ map — the visual centerpiece of the Classifier page.

Uses Plotly's WebGL-backed scattermapbox (via `carto-positron`, which needs
no Mapbox token) so it can comfortably render the full ~150k-row grid
without falling over like SVG-based marker maps would.

Supports click-to-inspect: selecting a point returns its row so the
Point Inspector component below the map can show full per-pixel detail.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.colors import CATEGORY_COLORS, CATEGORY_ORDER


def render_pfz_map(df: pd.DataFrame, category_col: str = "PFZ", key: str = "pfz_map"):
    """
    Renders the interactive map and returns the selected row (pd.Series)
    if the user has clicked a point, else None.
    """
    if df.empty:
        st.info("No data to display for the current filter selection.")
        return None

    center_lat = df["Latitude"].mean()
    center_lon = df["Longitude"].mean()

    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color=category_col,
        color_discrete_map=CATEGORY_COLORS,
        category_orders={category_col: CATEGORY_ORDER},
        hover_data={
            "Latitude": ":.3f",
            "Longitude": ":.3f",
            "SST": ":.2f" if "SST" in df.columns else False,
            "CHL": ":.3f" if "CHL" in df.columns else False,
            category_col: False,
        },
        zoom=4.2,
        height=560,
        opacity=0.75,
    )
    fig.update_traces(marker=dict(size=6))
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": center_lat, "lon": center_lon},
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            title=category_col,
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="left", x=0,
        ),
    )

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        selection_mode="points",
        key=key,
    )

    selected_row = None
    if event and event.get("selection") and event["selection"].get("points"):
        pts = event["selection"]["points"]
        if pts:
            p = pts[0]
            # Map the clicked point back to the source row via lat/lon match
            match = df[
                (df["Latitude"].round(5) == round(p["lat"], 5))
                & (df["Longitude"].round(5) == round(p["lon"], 5))
            ]
            if not match.empty:
                selected_row = match.iloc[0]

    return selected_row
