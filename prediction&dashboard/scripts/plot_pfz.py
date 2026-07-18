import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.lines import Line2D
import xarray as xr
from config import OUTPUT_PATH
import os


def plot_pfz(ds,OUTPUT_PATH,selected_date):

    # ----------------------------
    # Read NetCDF
    # ----------------------------
    

    sst = ds["SST"].values
    pfz = ds["PFZ"].values
    front = ds["Front_Present"].values

    lon = ds["longitude"].values
    lat = ds["latitude"].values

    Lon, Lat = np.meshgrid(lon, lat)

    # ----------------------------
    # Masks
    # ----------------------------
    mask_low = (pfz == 0) & (front == 1)
    mask_med = (pfz == 1) & (front == 1)
    mask_high = (pfz == 2) & (front == 1)

    # ----------------------------
    # Figure
    # ----------------------------
    fig = plt.figure(figsize=(14,10))

    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_extent(
        [
            lon.min(),
            lon.max(),
            lat.min(),
            lat.max()
        ],
        crs=ccrs.PlateCarree()
    )

    # ----------------------------
    # SST
    # ----------------------------
    pcm = ax.pcolormesh(
        Lon,
        Lat,
        sst,
        cmap="RdYlBu_r",
        shading="auto",
        transform=ccrs.PlateCarree(),
        zorder=1
    )

    # ----------------------------
    # Land
    # ----------------------------
    ax.add_feature(
        cfeature.LAND,
        facecolor="#d2c2a5",
        edgecolor="black",
        zorder=2
    )

    ax.coastlines(
        resolution="10m",
        linewidth=0.8,
        zorder=3
    )

    # ----------------------------
    # PFZ
    # ----------------------------
    ax.scatter(
        Lon[mask_low],
        Lat[mask_low],
        color="#F57C00",
        s=18,
        edgecolors="black",
        linewidths=0.2,
        transform=ccrs.PlateCarree(),
        rasterized=True,
        zorder=5)

    ax.scatter(
        Lon[mask_med],
        Lat[mask_med],
        color="#FFD54F",
        s=18,
        edgecolors="black",
        linewidths=0.2,
        transform=ccrs.PlateCarree(),
        rasterized=True,
        zorder=5)
    ax.scatter(
        Lon[mask_high],
        Lat[mask_high],
        color="#2E7D32",
        s=18,
        edgecolors="black",
        linewidths=0.2,
        transform=ccrs.PlateCarree(),
        rasterized=True,
        zorder=5)

    # ----------------------------
    # Colorbar
    # ----------------------------
    cbar = plt.colorbar(
        pcm,
        ax=ax,
        shrink=0.85,
        pad=0.02
    )

    cbar.set_label("Sea Surface Temperature (°C)")

    # ----------------------------
    # Grid
    # ----------------------------
    gl = ax.gridlines(
        draw_labels=True,
        linestyle="--",
        linewidth=0.5,
        alpha=0.5
    )

    gl.top_labels = False
    gl.right_labels = False

    gl.xlocator = mticker.FixedLocator(np.arange(65,97,5))
    gl.ylocator = mticker.FixedLocator(np.arange(5,25,5))

    # ----------------------------
    # Legend
    # ----------------------------
    legend = [

        Line2D([0],[0],
               marker='o',
               color='w',
               markerfacecolor='#F57C00',
               markersize=8,
               label='Low'),

        Line2D([0],[0],
               marker='o',
               color='w',
               markerfacecolor='#FFD54F',
               markersize=8,
               label='Medium'),

        Line2D([0],[0],
               marker='o',
               color='w',
               markerfacecolor='#2E7D32',
               markersize=8,
               label='High')

    ]

    ax.legend(
        handles=legend,
        loc="lower left",
        title="PFZ Class",
        framealpha=1
    )

    plt.title("Potential Fishing Zone Prediction")

    plt.savefig(
        os.path.join(
            OUTPUT_PATH,
            f"PFZ_Output_{selected_date}.png"
        ),
        dpi=600,
        bbox_inches="tight"
    )