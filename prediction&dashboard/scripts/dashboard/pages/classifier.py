"""
Classifier — pick a date, run or load the PFZ prediction, and inspect it.

Per project decision, PFZ classification is only meaningful on
thermal-front candidate pixels, so every view on this page (map, KPIs,
table, overlay) operates on the Front_Present == 1 subset only.

Layout: KPIs sit above; the interactive point map and the SST/PFZ
NetCDF overlay sit side by side as the visual centerpiece; the results
table + point inspector sit below.
"""
import time
from datetime import date
import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(CURRENT_DIR)
SCRIPTS_DIR = os.path.dirname(DASHBOARD_DIR)

for path in [CURRENT_DIR, DASHBOARD_DIR, SCRIPTS_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)
import streamlit as st

from config import OUTPUT_PATH
from Utils.date_utils import get_available_date_range
from Utils.output_exists import output_exists
from Utils.output_loader import load_outputs
from run_pipeline import main as run_pipeline_main

from components.theme import header_bar
from components.kpi_cards import render_kpi_row
from components.map_view import render_pfz_map
from components.nc_plot import render_sst_pfz_overlay
from components.point_inspector import render_point_inspector
from components.progress_tracker import ProgressTracker
from components.data_prep import filter_front_present
from components.colors import CATEGORY_ORDER

header_bar(
    "Classifier",
    "Select a date, generate or load its PFZ classification, and explore the results.",
)

# --- Date selection -----------------------------------------------------
try:
    min_date, max_date = get_available_date_range()
except Exception as e:
    st.error(f"Could not determine the available date range from the ocean datasets: {e}")
    st.stop()

col_date, col_status = st.columns([2, 3])
with col_date:
    selected_date: date = st.date_input(
        "Prediction date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )

# Reset stale session state if the user switched to a different date
if st.session_state.get("prediction_date") != selected_date:
    st.session_state["prediction_completed"] = False
    st.session_state["prediction_df"] = None
    st.session_state["prediction_png"] = None
    st.session_state["prediction_csv"] = None
    st.session_state["prediction_nc"] = None
    st.session_state["runtime"] = None
    st.session_state["prediction_date"] = selected_date

already_exists = output_exists(OUTPUT_PATH, selected_date)

with col_status:
    if already_exists:
        st.success(f"Cached prediction found for {selected_date}.", icon="✅")
    else:
        st.warning(f"No prediction exists yet for {selected_date}.", icon="⏳")

# --- Load cached or run pipeline ----------------------------------------
if already_exists and not st.session_state["prediction_completed"]:
    outputs = load_outputs(OUTPUT_PATH, selected_date)
    st.session_state["prediction_df"] = outputs["df"]
    st.session_state["prediction_png"] = outputs["png"]
    st.session_state["prediction_csv"] = outputs["csv"]
    st.session_state["prediction_nc"] = outputs["nc"]
    st.session_state["prediction_completed"] = True

if not already_exists:
    if st.button("Generate Prediction", type="primary", disabled=st.session_state["prediction_running"]):
        st.session_state["prediction_running"] = True
        st.session_state["prediction_completed"] = False
        st.rerun()

    if st.session_state["prediction_running"]:
        st.markdown("#### Running classifier pipeline")
        tracker = ProgressTracker()
        start = time.time()
        run_pipeline_main(selected_date, progress_callback=tracker.update)
        tracker.finish()
        st.session_state["runtime"] = round(time.time() - start, 1)

        outputs = load_outputs(OUTPUT_PATH, selected_date)
        st.session_state["prediction_df"] = outputs["df"]
        st.session_state["prediction_png"] = outputs["png"]
        st.session_state["prediction_csv"] = outputs["csv"]
        st.session_state["prediction_nc"] = outputs["nc"]
        st.session_state["prediction_completed"] = True
        st.session_state["prediction_running"] = False
        st.rerun()

# --- Results -------------------------------------------------------------
raw_df = st.session_state.get("prediction_df")

if raw_df is not None and st.session_state.get("prediction_completed"):
    st.divider()

    front_df = filter_front_present(raw_df)
    st.caption(
        f"Showing {len(front_df):,} thermal-front candidate pixels "
        f"(Front_Present == 1) out of {len(raw_df):,} total grid pixels."
    )

    # Filter state — shown clearly, applied consistently to the KPIs,
    # map, and table so counts never silently disagree.
    selected_categories = st.multiselect(
        "Filter by PFZ category", CATEGORY_ORDER, default=CATEGORY_ORDER,
    )
    filtered = front_df[front_df["PFZ"].isin(selected_categories)]
    if len(filtered) < len(front_df):
        st.caption(f"Category filter active — showing {len(filtered):,} of {len(front_df):,} front pixels.")

    counts = filtered["PFZ"].value_counts()
    kpis = [
        {"label": "Front Pixels (filtered)", "value": f"{len(filtered):,}"},
        {"label": "High Suitability", "value": f"{int(counts.get('High', 0)):,}"},
        {"label": "Medium Suitability", "value": f"{int(counts.get('Medium', 0)):,}"},
        {"label": "Low Suitability", "value": f"{int(counts.get('Low', 0)):,}"},
    ]
    if st.session_state.get("runtime"):
        kpis.append({"label": "Pipeline Runtime", "value": f"{st.session_state['runtime']}s"})
    render_kpi_row(kpis)

    st.write("")
    map_col, overlay_col = st.columns(2)
    with map_col:
        st.markdown("#### Interactive Map")
        selected_row = render_pfz_map(filtered, category_col="PFZ")
    with overlay_col:
        nc_path = st.session_state.get("prediction_nc")
        png_path = st.session_state.get("prediction_png")
        if nc_path:
            render_sst_pfz_overlay(nc_path, png_fallback_path=png_path)
        elif png_path:
            st.markdown("#### SST · PFZ Overlay")
            st.image(png_path, use_container_width=True)

    st.divider()
    left, right = st.columns([3, 2])
    with left:
        st.markdown("#### Results Table")
        display_cols = [
            "Date", "Latitude", "Longitude", "SST", "CHL", "Front_Present",
            "Depth", "Wind_Speed", "PFZ",
        ]
        display_cols = [c for c in display_cols if c in filtered.columns]
        st.dataframe(
            filtered[display_cols].reset_index(drop=True),
            use_container_width=True,
            height=340,
        )
        if st.session_state.get("prediction_csv"):
            with open(st.session_state["prediction_csv"], "rb") as f:
                st.download_button(
                    "Download full CSV", f.read(),
                    file_name=f"pfz_prediction_{selected_date}.csv",
                    use_container_width=True,
                )
    with right:
        render_point_inspector(selected_row)
