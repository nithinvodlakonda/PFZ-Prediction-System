from validate_files import validate_files
from load_data import load_all_datasets,standardize_dataset
from create_prediction_grid import create_prediction_grid
from remove_land import remove_land
from extractors.SST import extract_sst
from extractors.Current import extract_current
from extractors.Wind import extract_wind
from extractors.CHL import extract_chl
from extractors.SSS import extract_sss
from extractors.Depth import extract_depth
from extractors.Landing import extract_landing
from extractors.Front import extract_front
from extractors.Eddy import extract_eddy
from algorithms.cca import run_cca_on_netcdf
from extractors.Ekman import extract_ekman
from feature_engineering import feature_engineering
from predict import predict
from extractors.coast import extract_coast
from filter_candidate_pixels import filter_candidate_pixels
from config import OUTPUT_PATH
from PFZ_file import PFZ_file
from plot_pfz import plot_pfz
import numpy as np
import os
import pandas as pd
def update_progress(progress_callback, message):

    if progress_callback is not None:

        progress_callback(message)

def main(selected_date, progress_callback=None):
    selected_date = pd.to_datetime(selected_date)
    date_str=selected_date.strftime("%Y-%m-%d")

    # ==========================================================
    # STEP 1 : Validate Input Files
    # ==========================================================

    print("Step 1 : Validating files...")
    validation = validate_files(selected_date)
    update_progress(progress_callback, "Validate Input Files")

    # ==========================================================
    # STEP 2 : Load Datasets
    # ==========================================================

    print("Step 2 : Loading datasets...")
    datasets = load_all_datasets()
    date = validation["date"]

    for key in [
        "SST",
        "CURRENT",
        "CHL",
        "WIND",
        "SSS",
        "EKMAN"
    ]:
        datasets[key] = standardize_dataset(datasets[key])
        datasets[key] = datasets[key].sel(time=date)

    datasets["CYCLONIC"] = datasets["CYCLONIC"].where(
        datasets["CYCLONIC"]["time"] == np.datetime64(date),
        drop=True
    )

    datasets["ANTICYCLONIC"] = datasets["ANTICYCLONIC"].where(
        datasets["ANTICYCLONIC"]["time"] == np.datetime64(date),
        drop=True
    )

    update_progress(progress_callback, "Load Ocean Datasets")

    # ==========================================================
    # STEP 3 : Create Prediction Grid
    # ==========================================================

    print("Step 3 : Creating prediction grid...")
    df = create_prediction_grid(
        datasets["SST"],
        validation["date"]
    )

    update_progress(progress_callback, "Create Prediction Grid")

    # ==========================================================
    # STEP 4 : Remove Land Pixels
    # ==========================================================

    print("Step 4 : Removing land...")
    df = remove_land(df)

    update_progress(progress_callback, "Remove Land Pixels")

    # ==========================================================
    # STEP 5 : Run CCA Front Detection
    # ==========================================================

    print("Step 5 : Running CCA...")

    temp_sst = os.path.join(
        OUTPUT_PATH,
        "temp_sst.nc"
    )

    datasets["SST"].to_netcdf(temp_sst)

    front_ds = run_cca_on_netcdf(temp_sst)

    if os.path.exists(temp_sst):
        os.remove(temp_sst)

    front_ds.to_netcdf(
        os.path.join(
            OUTPUT_PATH,
            "fronts.nc"
        ),
        encoding={
            "front_magnitude": {
                "zlib": False,
                "dtype": "float64"
            },
            "front_present": {
                "zlib": False,
                "dtype": "float64"
            }
        }
    )

    update_progress(progress_callback, "Run CCA Front Detection")

    # ==========================================================
    # STEP 6 : Extract CHL
    # ==========================================================

    print("Step 6 : Extracting CHL...")
    df = extract_chl(datasets["CHL"], df)

    update_progress(progress_callback, "Extract Chlorophyll")

    # ==========================================================
    # STEP 7 : Extract Front
    # ==========================================================

    print("Step 7 : Extracting Front...")
    df = extract_front(front_ds, df)

    update_progress(progress_callback, "Extract Front Features")

    # ==========================================================
    # STEP 8 : Filter Candidate Pixels
    # ==========================================================

    print("Step 8 : Filtering candidate pixels...")
    df = filter_candidate_pixels(df)

    update_progress(progress_callback, "Filter Candidate Pixels")

    # ==========================================================
    # STEP 9 : Extract Depth
    # ==========================================================

    print("Step 9 : Extracting Depth...")
    df = extract_depth(datasets["DEPTH"], df)

    update_progress(progress_callback, "Extract Bathymetry")

    # ==========================================================
    # STEP 10 : Extract Ocean Current
    # ==========================================================

    print("Step 10 : Extracting Current...")
    df = extract_current(datasets["CURRENT"], df)

    update_progress(progress_callback, "Extract Ocean Currents")

    # ==========================================================
    # STEP 11 : Extract Wind
    # ==========================================================

    print("Step 11 : Extracting Wind...")
    df = extract_wind(datasets["WIND"], df)

    update_progress(progress_callback, "Extract Wind")

    # ==========================================================
    # STEP 12 : Extract SSS
    # ==========================================================

    print("Step 12 : Extracting SSS...")
    df = extract_sss(datasets["SSS"], df)

    update_progress(progress_callback, "Extract Sea Surface Salinity")

    # ==========================================================
    # STEP 13 : Extract Ekman
    # ==========================================================

    print("Step 13 : Extracting Ekman...")
    df = extract_ekman(
        datasets["EKMAN"],
        df
    )

    update_progress(progress_callback, "Extract Ekman Transport")

    # ==========================================================
    # STEP 14 : Extract SST
    # ==========================================================

    print("Step 14 : Extracting SST...")
    df = extract_sst(datasets["SST"], df)

    update_progress(progress_callback, "Extract Sea Surface Temperature")

    # ==========================================================
    # STEP 15 : Extract Coast
    # ==========================================================

    print("Step 15 : Extracting Coast...")
    df = extract_coast(
        datasets["COAST"],
        df
    )

    update_progress(progress_callback, "Extract Distance to Coast")

    # ==========================================================
    # STEP 16 : Extract Eddy
    # ==========================================================

    print("Step 16 : Extracting Eddy...")
    df = extract_eddy(
        datasets["CYCLONIC"],
        datasets["ANTICYCLONIC"],
        df
    )

    update_progress(progress_callback, "Extract Eddy Features")

    # ==========================================================
    # STEP 17 : Feature Engineering
    # ==========================================================

    print("Step 17 : Feature Engineering...")

    df = remove_land(df)
    df = feature_engineering(df)

    update_progress(progress_callback, "Feature Engineering")

    # ==========================================================
    # STEP 18 : Save Feature Dataset
    # ==========================================================

    today_file = os.path.join(
        OUTPUT_PATH,
        "today_features.csv"
    )

    df.to_csv(
        today_file,
        index=False
    )

    update_progress(progress_callback, "Save Feature Dataset")

    # ==========================================================
    # STEP 19 : Prediction
    # ==========================================================

    print("Step 19 : Running Prediction...")
    df = predict(df)

    update_progress(progress_callback, "Run Machine Learning Prediction")

    # ==========================================================
    # STEP 20 : Save Prediction CSV
    # ==========================================================

    run_folder = os.path.join(
        OUTPUT_PATH,
        date_str
    )

    os.makedirs(
        run_folder,
        exist_ok=True
    )

    prediction_csv = os.path.join(
        run_folder,
        f"pfz_prediction_{date_str}.csv"
    )
    
    df.to_csv(
        prediction_csv,
        index=False
    )

    update_progress(progress_callback, "Save Prediction CSV")

    # ==========================================================
    # STEP 21 : Create NetCDF
    # ==========================================================

    print("Step 21 : Creating NetCDF...")

    try:

        print("Creating xarray dataset...")

        pfz_ds = PFZ_file(
            df,
            datasets["SST"]
        )

        print("Dataset created successfully.")

        output_nc = os.path.join(
            run_folder,
            f"PFZ_Output_{date_str}.nc"
        )

        print("Saving NetCDF...")

        pfz_ds.to_netcdf(output_nc)

        print("NetCDF saved successfully.")

    except Exception as e:

        print("=" * 60)
        print("NETCDF ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 60)
        raise
    # ==========================================================
    # STEP 22 : Generate PFZ Map
    # ==========================================================

    print("Step 22 : Generating PFZ Map...")

    plot_pfz(
        pfz_ds,
        run_folder,
        date_str
    )

    update_progress(progress_callback, "Generate PFZ Map")

    print("Pipeline completed successfully.")
