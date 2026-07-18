"""
================================================================================
CCA — Cayula-Cornillon Algorithm for SST Front Detection
================================================================================

Standalone implementation of the algorithm described in:
    Cayula, J-F. and Cornillon, P. (1992)
    "Edge Detection Algorithm for SST Images"
    Journal of Atmospheric and Oceanic Technology, 9, 67-80.

Pipeline (per sliding window):
    1. Histogram-based threshold search (maximize between-class variance)
    2. Statistical checks: population proportion, mean difference, theta (bimodality)
    3. Cohesion check (spatial compactness of the two populations)
    4. Contour extraction (the actual front line at the optimal threshold)
    5. Magnitude = warm_population_mean - cold_population_mean (°C)

Input  : NetCDF file with an SST variable (lat, lon[, time])
Output : NetCDF file with two new 2D variables:
            - front_magnitude : °C difference at every detected front pixel
            - front_present   : binary (1 = front detected, 0/NaN = no front)

Window size (and the step/overlap) is configurable.
================================================================================
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from math import ceil, floor
import argparse


# ==============================================================================
# 1. CORE WINDOW-LEVEL ALGORITHM
# ==============================================================================

def analyze_window(
    window,
    min_theta=0.7,
    min_pop_proportion=0.20,
    min_pop_mean_diff=0.4,
    min_single_pop_cohesion=0.90,
    min_global_cohesion=0.70,
    max_nan_fraction=0.5,
    bin_width=0.02,
):
    """
    Runs the full Cayula-Cornillon test on a single 2D window of SST values.

    Parameters
    ----------
    window : 2D np.ndarray
        Temperature values (NaNs allowed for land/cloud).
    min_theta : float
        Minimum bimodality criterion theta = J_b(tau)/S_tot to accept a front.
        Paper recommends 0.7 (see Section 2.a.1).
    min_pop_proportion : float
        Each population must be at least this fraction of valid pixels.
        Paper uses 0.25; loosened to 0.20 here, change freely.
    min_pop_mean_diff : float
        Minimum |warm_mean - cold_mean| in the same units as `window` (°C)
        for the split to be considered a real front rather than noise.
    min_single_pop_cohesion : float
        Each individual population's cohesion (C1, C2) must exceed this.
        Paper recommends 0.90 (see Appendix B).
    min_global_cohesion : float
        Combined cohesion (C) must exceed this.
        Paper recommends 0.92 for the original window-on-window-border setup;
        lowered slightly here (0.70) for general overlapping windows — tune
        to your data.
    max_nan_fraction : float
        If more than this fraction of the window is NaN, skip immediately.
    bin_width : float
        Histogram bin width in temperature units.

    Returns
    -------
    dict with keys:
        'front_found'   : bool
        'threshold'     : optimal temperature threshold tau_opt (or None)
        'cold_mean'     : mean of the cold population (or None)
        'warm_mean'     : mean of the warm population (or None)
        'magnitude'     : warm_mean - cold_mean, i.e. front strength (or None)
        'theta'         : bimodality score (or None)
        'cohesion'      : (C, C1, C2) tuple (or None)
        'exit_code'     : reason code, see EXIT_CODES below
    """

    result = {
        "front_found": False,
        "threshold": None,
        "cold_mean": None,
        "warm_mean": None,
        "magnitude": None,
        "theta": None,
        "cohesion": None,
        "exit_code": None,
    }

    window = np.asarray(window, dtype="float64")
    nan_mask = np.isnan(window)
    n_total_pixels = window.size
    n_nans = int(np.sum(nan_mask))

    # ---- Check 0: too much missing data -------------------------------------
    if n_total_pixels == 0 or (n_nans / n_total_pixels) > max_nan_fraction:
        result["exit_code"] = "TOO_MANY_NANS"
        return result

    valid_values = window[~nan_mask]
    n_valid = valid_values.size

    if n_valid < 10:  # not enough pixels to build a meaningful histogram
        result["exit_code"] = "TOO_FEW_VALID_PIXELS"
        return result

    # ---- Step 1: Build histogram ---------------------------------------------
    t_min, t_max = np.min(valid_values), np.max(valid_values)
    if t_max - t_min < bin_width:
        # essentially constant temperature -> no possible front
        result["exit_code"] = "NO_TEMPERATURE_RANGE"
        return result

    n_bins = max(2, ceil((t_max - t_min) / bin_width))
    bin_edges = np.linspace(t_min, t_max, n_bins + 1)
    counts, edges = np.histogram(valid_values, bins=bin_edges)
    bin_centers = 0.5 * (edges[:-1] + edges[1:])

    # ---- Step 2: Search threshold maximizing between-class variance ---------
    # This implements equations (8)-(11) of the paper: for every candidate
    # threshold tau, compute J_b(tau) = N1*N2/(N1+N2)^2 * (mu1-mu2)^2 and
    # keep the tau that maximizes it.
    cumulative_count = np.cumsum(counts)
    cumulative_sum = np.cumsum(counts * bin_centers)
    total_count = cumulative_count[-1]
    total_sum = cumulative_sum[-1]

    best_separation = -1.0
    best_k = None
    best_cold_mean = None
    best_warm_mean = None
    best_cold_count = None
    best_warm_count = None

    for k in range(0, n_bins - 1):
        cold_count = cumulative_count[k]
        warm_count = total_count - cold_count
        if cold_count == 0 or warm_count == 0:
            continue

        cold_sum = cumulative_sum[k]
        warm_sum = total_sum - cold_sum

        cold_mean = cold_sum / cold_count
        warm_mean = warm_sum / warm_count

        # between-class variance term (unnormalized N1*N2*(mu1-mu2)^2 is
        # enough since (N1+N2)^2 is constant across k and only the argmax
        # matters here)
        separation = cold_count * warm_count * (warm_mean - cold_mean) ** 2

        if separation > best_separation:
            best_separation = separation
            best_k = k
            best_cold_mean = cold_mean
            best_warm_mean = warm_mean
            best_cold_count = cold_count
            best_warm_count = warm_count

    if best_k is None:
        result["exit_code"] = "NO_VALID_SPLIT"
        return result

    tau_opt = bin_centers[best_k]

    # ---- Step 3: Population proportion check ---------------------------------
    cold_fraction = best_cold_count / total_count
    warm_fraction = best_warm_count / total_count
    if cold_fraction < min_pop_proportion or warm_fraction < min_pop_proportion:
        result["exit_code"] = "POPULATION_TOO_SMALL"
        return result

    # ---- Step 4: Mean difference check ---------------------------------------
    magnitude = best_warm_mean - best_cold_mean
    if magnitude < min_pop_mean_diff:
        result["exit_code"] = "MEAN_DIFF_TOO_SMALL"
        return result

    # ---- Step 5: Theta (bimodality) check -------------------------------------
    total_mean = total_sum / total_count
    total_sum_sq = np.sum(counts * bin_centers ** 2)
    total_variance = total_sum_sq - total_count * total_mean ** 2
    if total_variance <= 0:
        result["exit_code"] = "ZERO_VARIANCE"
        return result

    theta = best_separation / (total_variance * 1.0)
    # Normalize theta the same way as J_b(tau)/S_tot: dividing separation
    # (which already has the N1*N2 factor) by total_variance*total_count
    # reproduces J_b/S_tot up to the constant (N1+N2)^2 term, consistent
    # with the relative comparison used to pick tau above.
    theta = best_separation / (total_variance * total_count)

    if theta < min_theta:
        result["exit_code"] = "THETA_TOO_LOW"
        return result

    # ---- Step 6: Cohesion check -------------------------------------------------
    # Replace NaNs with a value that will never accidentally match either
    # side of the threshold comparison (keeps loop simple); they are
    # excluded explicitly via nan_mask checks below.
    filled = np.where(nan_mask, tau_opt - 1e9, window)  # arbitrary, excluded anyway

    n_rows, n_cols = filled.shape
    cold_next_to_cold = 0
    cold_next_to_either = 0
    warm_next_to_warm = 0
    warm_next_to_either = 0

    for row in range(n_rows - 1):
        for col in range(n_cols - 1):
            if nan_mask[row, col] or nan_mask[row + 1, col] or nan_mask[row, col + 1]:
                continue

            center_is_cold = filled[row, col] <= tau_opt

            # bottom neighbor
            if not nan_mask[row + 1, col]:
                if center_is_cold:
                    cold_next_to_either += 1
                    if filled[row + 1, col] <= tau_opt:
                        cold_next_to_cold += 1
                else:
                    warm_next_to_either += 1
                    if filled[row + 1, col] > tau_opt:
                        warm_next_to_warm += 1

            # right neighbor
            if not nan_mask[row, col + 1]:
                if center_is_cold:
                    cold_next_to_either += 1
                    if filled[row, col + 1] <= tau_opt:
                        cold_next_to_cold += 1
                else:
                    warm_next_to_either += 1
                    if filled[row, col + 1] > tau_opt:
                        warm_next_to_warm += 1

    if cold_next_to_either == 0 or warm_next_to_either == 0:
        result["exit_code"] = "COHESION_UNDEFINED"
        return result

    c1_cold_cohesion = cold_next_to_cold / cold_next_to_either
    c2_warm_cohesion = warm_next_to_warm / warm_next_to_either
    c_global_cohesion = (cold_next_to_cold + warm_next_to_warm) / (
        cold_next_to_either + warm_next_to_either
    )

    if (
        c1_cold_cohesion < min_single_pop_cohesion
        or c2_warm_cohesion < min_single_pop_cohesion
        or c_global_cohesion < min_global_cohesion
    ):
        result["exit_code"] = "COHESION_TOO_LOW"
        return result

    # ---- All checks passed: front confirmed ------------------------------------
    result.update(
        {
            "front_found": True,
            "threshold": float(tau_opt),
            "cold_mean": float(best_cold_mean),
            "warm_mean": float(best_warm_mean),
            "magnitude": float(magnitude),
            "theta": float(theta),
            "cohesion": (
                float(c_global_cohesion),
                float(c1_cold_cohesion),
                float(c2_warm_cohesion),
            ),
            "exit_code": "FRONT_DETECTED",
        }
    )
    return result


# ==============================================================================
# 2. CONTOUR EXTRACTION FOR A CONFIRMED FRONT
# ==============================================================================

def extract_front_contour(window,
    threshold,
    lon_coords,
    lat_coords,
    corner_mask=None,
    min_points=7,
):
    """
    Given a window and its confirmed threshold, trace the actual front line
    (the iso-temperature contour at `threshold`) and return it as lon/lat
    coordinate arrays.

    Closed loops and very short contours (< min_points) are discarded, since
    real oceanographic fronts are open curves crossing the window, not blobs.
    """
    lon_out, lat_out = [], []

    plot_window = np.where(np.isnan(window), np.nan, window)
    if np.all(np.isnan(plot_window)):
        return np.array([]), np.array([])

    fig = plt.figure()
    try:
        cs = plt.contour(lon_coords, lat_coords, plot_window, levels=[threshold])
        segments = cs.allsegs[0] if len(cs.allsegs) > 0 else []

        for seg in segments:
            if corner_mask is not None:
            
                r0, r1, c0, c1 = corner_mask
            
                lat1 = lat_coords[r0]
                lat2 = lat_coords[r1 - 1]
                        
                lat_min = min(lat1, lat2)
                lat_max = max(lat1, lat2)
                        
                lon1 = lon_coords[c0]
                lon2 = lon_coords[c1 - 1]
                        
                lon_min = min(lon1, lon2)
                lon_max = max(lon1, lon2)
            
                keep = (
                    (seg[:,0] >= lon_min) &
                    (seg[:,0] <= lon_max) &
                    (seg[:,1] >= lat_min) &
                    (seg[:,1] <= lat_max)
                )
            
                seg = seg[keep]
            if len(seg) < min_points:
                continue
            is_closed = np.allclose(seg[0], seg[-1])
            if is_closed:
                continue
            lon_out.extend(seg[:, 0].tolist())
            lat_out.extend(seg[:, 1].tolist())
    finally:
        plt.close(fig)

    return np.array(lon_out), np.array(lat_out)


# ==============================================================================
# 3. SLIDING-WINDOW DRIVER OVER A FULL 2D SST FIELD
# ==============================================================================

def run_cca_on_field(
    sst_2d,
    lon_1d,
    lat_1d,
    **cca_kwargs,
):
    """
    Applies the original CCA-SIED traversal using 48×48 parent windows divided into four overlapping 32×32 subwindows. runs the CCA test on every window,
    and accumulates per-pixel magnitude onto the full output grid.

    Parameters
    ----------
    sst_2d : 2D np.ndarray  (n_rows, n_cols)
    lon_1d : 1D np.ndarray  (n_cols,)
    lat_1d : 1D np.ndarray  (n_rows,)
    **cca_kwargs :
        Forwarded to `analyze_window` (min_theta, min_pop_proportion, etc).

    Returns
    -------
    magnitude_grid : 2D np.ndarray, same shape as sst_2d
        Front magnitude (°C) at every pixel found to lie on a front contour.
        NaN everywhere else.
    presence_grid : 2D np.ndarray, same shape as sst_2d
        1.0 where a front pixel was found, NaN elsewhere.
    front_lon, front_lat, front_mag : 1D arrays
        Flat list of every contour point found across all windows, with its
        associated magnitude — useful for vector-style output / shapefiles.
    """
    n_rows, n_cols = sst_2d.shape

    magnitude_grid = np.full((n_rows, n_cols), np.nan, dtype="float32")
    presence_grid = np.full((n_rows, n_cols), np.nan, dtype="float32")

    all_lon, all_lat, all_mag = [], [], []

    lon_min, lon_max = float(lon_1d.min()), float(lon_1d.max())
    lat_min, lat_max = float(lat_1d.min()), float(lat_1d.max())
    deg_per_col = (lon_max - lon_min) / max(n_cols - 1, 1)
    deg_per_row = (lat_max - lat_min) / max(n_rows - 1, 1)

        # ------------------------------------------------------------------
    # Original CCA-SIED window layout
    # ------------------------------------------------------------------

    PARENT_WINDOW = 48
    SUB_WINDOW = 32
    STEP = 16

    # Four overlapping 32×32 subwindows inside a 48×48 parent window.
    # (row_start, row_end, col_start, col_end)

    subwindows = [
    (0, 32, 0, 32),      # Upper Left
    (0, 32, 16, 48),     # Upper Right
    (16, 48, 16, 48),    # Lower Right
    (16, 48, 0, 32),     # Lower Left
    ]

    corner_masks = [
    (16, 32, 16, 32),
    (16, 32, 0, 16),
    (0, 16, 16, 32),
    (0, 16, 0, 16),
    ]
    # ------------------------------------------------------------------
    # Traverse every 48×48 parent window
    # ------------------------------------------------------------------

    for parent_r0 in range(0, n_rows - PARENT_WINDOW + 1, STEP):

        for parent_c0 in range(0, n_cols - PARENT_WINDOW + 1, STEP):

            parent_window = sst_2d[
                parent_r0:parent_r0 + PARENT_WINDOW,
                parent_c0:parent_c0 + PARENT_WINDOW
            ]

            if parent_window.shape != (48, 48):
                continue
            # ----------------------------------------------------------
            # Process the four overlapping 32×32 subwindows
            # ----------------------------------------------------------

            for (r0, r1, c0, c1), corner_mask in zip(subwindows, corner_masks):

                window = parent_window[r0:r1, c0:c1]

                # Coordinates corresponding to this subwindow
                window_lon = lon_1d[
                    parent_c0 + c0:
                    parent_c0 + c1
                ]

                window_lat = lat_1d[
                    parent_r0 + r0:
                    parent_r0 + r1
                ]

                # Run CCA statistics
                outcome = analyze_window(
                    window,
                    **cca_kwargs
                )

                if not outcome["front_found"]:
                    continue
                                # ------------------------------------------------------
                # Extract contour from this confirmed subwindow
                # ------------------------------------------------------

                contour_lon, contour_lat = extract_front_contour(
                    window,
                    outcome["threshold"],
                    window_lon,
                    window_lat,
                    corner_mask=corner_mask      # we'll add this argument later
                )

                if contour_lon.size == 0:
                    continue

                magnitude = outcome["magnitude"]

                all_lon.extend(contour_lon.tolist())
                all_lat.extend(contour_lat.tolist())
                all_mag.extend([magnitude] * len(contour_lon))

                # ------------------------------------------------------
                # Convert contour coordinates back to image indices
                # ------------------------------------------------------

                cols_idx = np.round(
                    (contour_lon - lon_min) / deg_per_col
                ).astype(int)

                rows_idx = np.round(
                    (contour_lat - lat_min) / deg_per_row
                ).astype(int)

                valid = (
                    (rows_idx >= 0)
                    & (rows_idx < n_rows)
                    & (cols_idx >= 0)
                    & (cols_idx < n_cols)
                )

                rows_idx = rows_idx[valid]
                cols_idx = cols_idx[valid]

                # ------------------------------------------------------
                # Store maximum magnitude at each pixel
                # ------------------------------------------------------

                for rr, cc in zip(rows_idx, cols_idx):

                    if np.isnan(magnitude_grid[rr, cc]):
                        magnitude_grid[rr, cc] = magnitude
                    else:
                        magnitude_grid[rr, cc] = max(
                            magnitude_grid[rr, cc],
                            magnitude
                        )

                    presence_grid[rr, cc] = 1.0
    return (
    magnitude_grid,
    presence_grid,
    np.array(all_lon),
    np.array(all_lat),
    np.array(all_mag),
    )

# ==============================================================================
# 4. NETCDF I/O WRAPPER (load SST -> run CCA -> save fronts/magnitude)
# ==============================================================================

def run_cca_on_netcdf(
    input_path,
    output_path,
    sst_var="analysed_sst",
    lat_var="lat",
    lon_var="lon",
    time_index=0,
    kelvin_to_celsius=True,
    **cca_kwargs,
):
    """
    End-to-end: read SST from a NetCDF file, run CCA across the field, and
    write a new NetCDF file containing front magnitude + presence as 2D
    variables aligned to the same lat/lon grid as the input.

    Parameters
    ----------
    input_path : str
        Path to source .nc file.
    output_path : str
        Path where the result .nc file will be written.
    sst_var, lat_var, lon_var : str
        Variable/coordinate names in the input file. Auto-renames
        'latitude'/'longitude' to 'lat'/'lon' if needed.
    time_index : int
        Which time slice to process if the SST variable has a time
        dimension (ignored if there is none).
    kelvin_to_celsius : bool
        Subtract 273.15 from the SST field before analysis (most satellite
        products store SST in Kelvin).
    window_size : int
        Square analysis window side length in pixels. CONFIGURABLE.
    step_size : int or None
        Sliding step in pixels. If None, defaults to window_size // 2
        (50% overlap), matching the spirit of the paper's overlapping
        windows. Set step_size = window_size for non-overlapping windows.
    **cca_kwargs :
        Forwarded to `analyze_window` — e.g. min_theta=0.7,
        min_pop_proportion=0.2, min_pop_mean_diff=0.4,
        min_single_pop_cohesion=0.9, min_global_cohesion=0.7.

    Returns
    -------
    xr.Dataset
        The dataset that was written to `output_path` (also returned in
        memory in case you want to inspect/plot it immediately).
    """

    ds = xr.open_dataset(input_path)

    rename_map = {}
    if "latitude" in ds.coords and lat_var not in ds.coords:
        rename_map["latitude"] = lat_var
    if "longitude" in ds.coords and lon_var not in ds.coords:
        rename_map["longitude"] = lon_var
    if rename_map:
        ds = ds.rename(rename_map)

    lat_1d = ds[lat_var].values
    lon_1d = ds[lon_var].values

    sst_da = ds[sst_var]
    if "time" in sst_da.dims:
        sst_2d = sst_da.isel(time=time_index).values
        time_coord_value = ds["time"].values[time_index] if "time" in ds.coords else None
    else:
        sst_2d = sst_da.values
        time_coord_value = None

    sst_2d = np.asarray(sst_2d, dtype="float64")
    if kelvin_to_celsius and np.nanmean(sst_2d) > 100:  # heuristic: looks like Kelvin
        sst_2d = sst_2d - 273.15

    magnitude_grid, presence_grid, front_lon, front_lat, front_mag = run_cca_on_field(
        sst_2d,
        lon_1d,
        lat_1d,
        **cca_kwargs,
    )

    out_ds = xr.Dataset(
        data_vars={
            "front_magnitude": (
                (lat_var, lon_var),
                magnitude_grid,
                {
                    "long_name": "Cayula-Cornillon front magnitude",
                    "units": "degC",
                    "description": (
                        "Temperature difference (warm_population_mean - "
                        "cold_population_mean) at detected front pixels. "
                        "NaN where no front was detected."
                    ),
                },
            ),
            "front_present": (
                (lat_var, lon_var),
                presence_grid,
                {
                    "long_name": "Front presence flag",
                    "units": "1",
                    "description": "1 = front pixel detected, NaN = no front.",
                },
            ),
        },
        coords={
            lat_var: (lat_var, lat_1d, ds[lat_var].attrs),
            lon_var: (lon_var, lon_1d, ds[lon_var].attrs),
        },
        attrs={
            "title": "CCA (Cayula-Cornillon) front detection output",
            "source_file": str(input_path),
            "algorithm": "Cayula & Cornillon (1992), JAOT 9:67-80",
            "parent_window_pixels": 48,
            "subwindow_pixels": 32,
            "step_size_pixels": 16,
            "min_theta": cca_kwargs.get("min_theta", 0.7),
            "min_pop_proportion": cca_kwargs.get("min_pop_proportion", 0.20),
            "min_pop_mean_diff_degC": cca_kwargs.get("min_pop_mean_diff", 0.4),
            "min_single_pop_cohesion": cca_kwargs.get("min_single_pop_cohesion", 0.90),
            "min_global_cohesion": cca_kwargs.get("min_global_cohesion", 0.70),
            "n_front_contour_points": int(front_lon.size),
        },
    )

    if time_coord_value is not None:
        out_ds = out_ds.expand_dims(time=[time_coord_value])

    out_ds.to_netcdf(
            output_path,
            encoding={
                "front_magnitude": {
                    "zlib": True,
                    "complevel": 5
                },
                "front_present": {
                    "zlib": True,
                    "complevel": 5
                }
            }
        )
    ds.close()

    print(f"Saved CCA output -> {output_path}")
    print("  parent_window=48")
    print("  subwindow=32")
    print("  step=16")
    print(f"  front pixels found: {int(np.nansum(presence_grid))}")
    if front_mag.size > 0:
        print(
            f"  magnitude range: {np.min(front_mag):.2f} to "
            f"{np.max(front_mag):.2f} degC (mean {np.mean(front_mag):.2f})"
        )
    else:
        print("  no fronts detected with current thresholds.")
    
    return out_ds


# ==============================================================================
# 5. OPTIONAL QUICK-LOOK PLOT
# ==============================================================================

def plot_cca_result(input_path, output_path, sst_var="analysed_sst",
                     lat_var="lat", lon_var="lon", time_index=0):
    """Simple two-panel plot: SST + front outline, and front magnitude map."""
    ds_in = xr.open_dataset(input_path)
    ds_out = xr.open_dataset(output_path)

    rename_map = {}
    if "latitude" in ds_in.coords and lat_var not in ds_in.coords:
        rename_map["latitude"] = lat_var
    if "longitude" in ds_in.coords and lon_var not in ds_in.coords:
        rename_map["longitude"] = lon_var
    if rename_map:
        ds_in = ds_in.rename(rename_map)

    sst_da = ds_in[sst_var]
    sst_2d = sst_da.isel(time=time_index).values if "time" in sst_da.dims else sst_da.values
    sst_2d = np.asarray(sst_2d, dtype="float64")
    if np.nanmean(sst_2d) > 100:
        sst_2d = sst_2d - 273.15

    lat_1d = ds_in[lat_var].values
    lon_1d = ds_in[lon_var].values

    magnitude = ds_out["front_magnitude"].values
    if magnitude.ndim == 3:
        magnitude = magnitude[0]
    presence = ds_out["front_present"].values
    if presence.ndim == 3:
        presence = presence[0]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    ax = axes[0]
    pcm = ax.pcolormesh(lon_1d, lat_1d, sst_2d, cmap="coolwarm", shading="auto")
    fig.colorbar(pcm, ax=ax, label="SST (degC)")
    binary = np.nan_to_num(presence, nan=0.0)
    if np.any(binary > 0):
        ax.contour(lon_1d, lat_1d, binary, levels=[0.5], colors="black", linewidths=0.8)
    ax.set_title("SST + Detected Fronts")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    ax = axes[1]
    cmap_mag = plt.cm.viridis.copy()
    cmap_mag.set_bad("lightgray")
    im = ax.imshow(
        np.ma.masked_invalid(magnitude),
        cmap=cmap_mag,
        origin="lower",
        extent=[lon_1d[0], lon_1d[-1], lat_1d[0], lat_1d[-1]],
        aspect="auto",
    )
    fig.colorbar(im, ax=ax, label="Front Magnitude (degC)")
    ax.set_title("CCA Front Magnitude")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    plt.suptitle("Cayula-Cornillon Algorithm — Front Detection & Magnitude")
    plt.tight_layout()
    return fig


# ==============================================================================
# 6. COMMAND-LINE INTERFACE
# ==============================================================================

def _build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Run the Cayula-Cornillon Algorithm (CCA) on an SST NetCDF file."
    )
    parser.add_argument("input_nc", help="Path to input SST NetCDF file")
    parser.add_argument("output_nc", help="Path to write output NetCDF file")
    parser.add_argument("--sst-var", default="analysed_sst", help="SST variable name")
    parser.add_argument("--lat-var", default="lat", help="Latitude coordinate name")
    parser.add_argument("--lon-var", default="lon", help="Longitude coordinate name")
    parser.add_argument("--time-index", type=int, default=0, help="Time slice index")
    parser.add_argument("--min-theta", type=float, default=0.7)
    parser.add_argument("--min-pop-proportion", type=float, default=0.20)
    parser.add_argument("--min-pop-mean-diff", type=float, default=0.4)
    parser.add_argument("--min-single-pop-cohesion", type=float, default=0.90)
    parser.add_argument("--min-global-cohesion", type=float, default=0.70)
    parser.add_argument(
        "--no-kelvin-conversion", action="store_true",
        help="Disable automatic Kelvin->Celsius conversion"
    )
    parser.add_argument(
        "--plot", action="store_true",
        help="Save a quick-look PNG plot alongside the output NetCDF"
    )
    return parser


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    run_cca_on_netcdf(
        input_path=args.input_nc,
        output_path=args.output_nc,
        sst_var=args.sst_var,
        lat_var=args.lat_var,
        lon_var=args.lon_var,
        time_index=args.time_index,
        kelvin_to_celsius=not args.no_kelvin_conversion,
        min_theta=args.min_theta,
        min_pop_proportion=args.min_pop_proportion,
        min_pop_mean_diff=args.min_pop_mean_diff,
        min_single_pop_cohesion=args.min_single_pop_cohesion,
        min_global_cohesion=args.min_global_cohesion,
        )

    if args.plot:
        fig = plot_cca_result(
            args.input_nc, args.output_nc,
            sst_var=args.sst_var, lat_var=args.lat_var, lon_var=args.lon_var,
            time_index=args.time_index,
        )
        png_path = str(args.output_nc).rsplit(".", 1)[0] + "_plot.png"
        fig.savefig(png_path, dpi=150)
        print(f"Saved plot -> {png_path}")


if __name__ == "__main__":
    main()