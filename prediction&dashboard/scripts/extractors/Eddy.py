import numpy as np
import xarray as xr

def build_eddy_dataset(cyclonic_ds, anticyclonic_ds):
    """
    Merge cyclonic and anticyclonic eddies.
    """

    eddy_ds = xr.concat(
        [cyclonic_ds, anticyclonic_ds],
        dim="obs"
    )

    eddy_ds["Type"] = (
        "obs",
        np.concatenate([
            np.ones(cyclonic_ds.sizes["obs"], dtype=np.int8),
            -np.ones(anticyclonic_ds.sizes["obs"], dtype=np.int8)
        ])
    )

    return eddy_ds
from shapely.geometry import Polygon
import numpy as np

def build_polygon_cache(eddy_ds):
    """
    Build all eddy polygons once.
    """

    contour_lon = eddy_ds["effective_contour_longitude"].values
    contour_lat = eddy_ds["effective_contour_latitude"].values

    polygon_cache = {}

    for obs in range(eddy_ds.sizes["obs"]):

        lons = contour_lon[obs]
        lats = contour_lat[obs]

        mask = (
            ~np.isnan(lons) &
            ~np.isnan(lats)
        )

        lons = lons[mask]
        lats = lats[mask]

        if len(lons) < 3:
            continue

        try:
            polygon_cache[obs] = Polygon(zip(lons, lats))
        except Exception:
            continue

    return polygon_cache
from sklearn.neighbors import BallTree
import numpy as np

EARTH_RADIUS = 6371.0

def build_ball_tree(eddy_ds):
    """
    Build BallTree from eddy centres.
    """

    coords = np.deg2rad(
        np.column_stack((
            eddy_ds["latitude"].values,
            eddy_ds["longitude"].values
        ))
    )

    tree = BallTree(
        coords,
        metric="haversine"
    )

    return tree

from shapely.geometry import Point
import numpy as np


def extract_eddy(cyclonic_ds, anticyclonic_ds, df):
    """
    Extract eddy features.
    """

    # -----------------------------
    # Build eddy dataset
    # -----------------------------
    eddy_ds = build_eddy_dataset(
        cyclonic_ds,
        anticyclonic_ds
    )

    polygon_cache = build_polygon_cache(
        eddy_ds
    )

    tree = build_ball_tree(
        eddy_ds
    )

    # -----------------------------
    # Query ALL prediction points
    # -----------------------------
    coords = np.deg2rad(
        df[["Latitude", "Longitude"]].values
    )

    dist, ind = tree.query(
        coords,
        k=5
    )

    inside = []
    distance = []
    etype = []

    # -----------------------------
    # Loop only once
    # -----------------------------
    for i, row in enumerate(df.itertuples(index=False)):

        point = Point(
            row.Longitude,
            row.Latitude
        )

        flag = 0

        # Check only nearest 5 eddies
        for obs in ind[i]:

            polygon = polygon_cache.get(obs)

            if polygon is not None and polygon.contains(point):

                flag = 1
                break

        inside.append(flag)

        distance.append(
            dist[i][0] * EARTH_RADIUS
        )

        etype.append(
            eddy_ds["Type"].values[ind[i][0]]
        )

    df["Inside_Eddy"] = inside

    df["Nearest_Eddy_Distance_km"] = distance

    df["Nearest_Eddy_Type"] = etype

    return df