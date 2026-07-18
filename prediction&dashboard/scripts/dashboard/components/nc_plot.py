"""
SST + PFZ overlay — reads directly from PFZ_Output_{date}.nc (written by
the production PFZ_file() step: a 2D lat/lon grid with SST, PFZ (coded
0=Low/1=Medium/2=High), and Front_Present variables).

Renders SST as a background heatmap with PFZ category markers drawn
ONLY over cells where Front_Present == 1, per project decision — this
sits beside the interactive map on the Classifier page rather than
replacing it.

Falls back to the pre-rendered PFZ_Output_{date}.png if the NetCDF
can't be parsed for any reason, so the page never breaks because of it.
"""
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import xarray as xr

from components.colors import CATEGORY_COLORS

_CODE_TO_CATEGORY = {0: "Low", 1: "Medium", 2: "High"}


def render_sst_pfz_overlay(nc_path: str, png_fallback_path: str | None = None, key: str = "sst_pfz_overlay"):
    st.markdown("#### SST · PFZ Overlay (front pixels only)")
    try:
        _render_from_netcdf(nc_path, key)
    except Exception as e:
        st.caption(f"Could not render the NetCDF overlay ({e}); showing the saved output image instead.")
        if png_fallback_path:
            st.image(png_fallback_path, use_container_width=True)
        else:
            st.info("No fallback image available for this date.")


def _render_from_netcdf(nc_path: str, key: str):
    with xr.open_dataset(nc_path) as ds:
        lat = ds["latitude"].values
        lon = ds["longitude"].values
        sst = ds["SST"].values
        pfz_code = ds["PFZ"].values
        front = ds["Front_Present"].values

    fig = go.Figure()

    # SST background heatmap
    fig.add_trace(go.Heatmap(
        z=sst, x=lon, y=lat,
        colorscale="RdYlBu_r",
        colorbar=dict(title="SST (°C)", len=0.75),
        opacity=0.85,
        hovertemplate="Lon %{x:.2f}<br>Lat %{y:.2f}<br>SST %{z:.2f}°C<extra></extra>",
    ))

    # PFZ markers, restricted to Front_Present == 1 cells only
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    front_mask = front == 1

    for code, category in _CODE_TO_CATEGORY.items():
        cat_mask = front_mask & (pfz_code == code)
        if not np.any(cat_mask):
            continue
        fig.add_trace(go.Scattergl(
            x=lon_grid[cat_mask], y=lat_grid[cat_mask],
            mode="markers",
            marker=dict(size=5, color=CATEGORY_COLORS[category],
                        line=dict(width=0.5, color="white")),
            name=category,
            hovertemplate=f"{category}<br>Lon %{{x:.2f}}<br>Lat %{{y:.2f}}<extra></extra>",
        ))

    fig.update_layout(
        height=560,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Longitude", yaxis_title="Latitude",
        legend=dict(title="PFZ (front pixels)", orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True, key=key)
