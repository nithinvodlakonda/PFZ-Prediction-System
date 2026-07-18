import numpy as np
from sklearn.neighbors import BallTree

EARTH_RADIUS = 6371.0  # km


def extract_coast(coast, df):
    """
    Fast coastline distance extraction using BallTree.

    Parameters
    ----------
    coast : GeoDataFrame
        Coastline shapefile.

    df : pandas.DataFrame
        Prediction dataframe.

    Returns
    -------
    pandas.DataFrame
    """

    print("Building coastline BallTree...")

    # Ensure WGS84 coordinates
    coast = coast.to_crs("EPSG:4326")

    # -------------------------------------------------------
    # Extract all coastline vertices
    # -------------------------------------------------------
    vertices = []

    for geom in coast.geometry:

        if geom is None:
            continue

        if geom.geom_type == "LineString":

            vertices.extend(geom.coords)

        elif geom.geom_type == "MultiLineString":

            for line in geom.geoms:
                vertices.extend(line.coords)

    vertices = np.asarray(vertices)

    # (lon, lat) -> (lat, lon)
    coast_latlon = np.column_stack(
        (
            vertices[:, 1],
            vertices[:, 0]
        )
    )

    # -------------------------------------------------------
    # Build BallTree
    # -------------------------------------------------------
    tree = BallTree(
        np.deg2rad(coast_latlon),
        metric="haversine"
    )

    print("Querying coastline distances...")

    # -------------------------------------------------------
    # Prediction points
    # -------------------------------------------------------
    points = df[["Latitude", "Longitude"]].values

    mask = (
        ~np.isnan(points[:, 0]) &
        ~np.isnan(points[:, 1])
    )

    distances = np.full(len(df), np.nan)

    dist, _ = tree.query(
        np.deg2rad(points[mask]),
        k=1
    )

    distances[mask] = dist[:, 0] * EARTH_RADIUS

    df["Distance_to_Coast_km"] = distances

    return df