"""
Home — hero + live system status + CTA, with About and Settings folded
in below as tabs (per project decision: no separate About/Settings pages).
"""
from datetime import date

import streamlit as st
import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(CURRENT_DIR)
SCRIPTS_DIR = os.path.dirname(DASHBOARD_DIR)

for path in [CURRENT_DIR, DASHBOARD_DIR, SCRIPTS_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)
from config import OUTPUT_PATH, DATA_PATH, MODEL_PATH, DATA_NC_PATH
from Utils.archive import get_prediction_archive
from Utils.output_exists import output_exists
from components.kpi_cards import render_kpi_row

# --- Hero -------------------------------------------------------------
st.markdown(
    """
    <div class="pfz-hero">
        <h1>PFZ Classifier System</h1>
        <p>Potential Fishing Zone classification for the Indian EEZ — combining
        satellite oceanographic data with an Extra Trees Classifier to flag
        High / Medium / Low suitability ocean grid pixels.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Live system status -------------------------------------------------
try:
    archive = get_prediction_archive(OUTPUT_PATH)
    backend_reachable = True
except Exception:
    archive = []
    backend_reachable = False

today_ready = output_exists(OUTPUT_PATH, date.today()) if backend_reachable else False

col_status, col_cta = st.columns([3, 1])
with col_status:
    if not backend_reachable:
        dot_color, status_text = "#dc3545", "Backend unreachable"
    elif today_ready:
        dot_color, status_text = "#28a745", "classification is ready"
    else:
        dot_color, status_text = "#ffc107", "classification not yet run"
    st.markdown(
        f'<span class="pfz-status-dot" style="background-color:{dot_color};"></span>'
        f'<strong>{status_text}</strong>',
        unsafe_allow_html=True,
    )
with col_cta:
    if st.button("Run PFZ Classifier →", use_container_width=True, type="primary"):
        st.switch_page("pages/classifier.py")

st.write("")
kpis = [
    {"label": "Archived Prediction Runs", "value": str(len(archive))},
    {
        "label": "Most Recent Run",
        "value": archive[0]["Date"] if archive else "—",
    },
    {
        "label": "System Status",
        "value": "Online" if backend_reachable else "Unreachable",
    },
]
render_kpi_row(kpis)

st.divider()

# --- About / Settings, folded into Home per project decision -----------
tab_about, tab_settings = st.tabs(["About", "Settings"])

with tab_about:
    st.markdown("### About the PFZ Classifier System")
    st.markdown(
        "Developed during a BSc Computer Science internship in the **Ocean "
        "Data Management (ODM) Division** at the **Indian National Centre "
        "for Ocean Information Services (INCOIS)**, Ministry of Earth "
        "Sciences, Government of India, under the project *Probabilistic "
        "Potential Fishing Zone (PFZ) Forecasting*."
    )

    st.markdown("#### What it does")
    st.markdown(
        "The system predicts probable fishing zones by combining "
        "satellite-derived oceanographic datasets with a machine learning "
        "model, classifying ocean grid pixels into **High / Medium / Low** "
        "fishing suitability (`PFZ` column)."
    )

    st.markdown("#### Ocean datasets used")
    c1, c2, c3 = st.columns(3)
    c1.markdown("- Sea Surface Temperature (SST)\n- Chlorophyll-a (CHL)\n- Sea Surface Salinity (SSS)")
    c2.markdown("- Ocean Currents\n- Wind\n- Ekman Transport")
    c3.markdown("- Bathymetry (Depth)\n- Sea Surface Height (SSH)\n- Eddy detection features")

    st.markdown("#### Model")
    st.markdown(
        "**Extra Trees Classifier** (scikit-learn) — multi-class "
        "classification over engineered oceanographic + front-detection "
        "features, trained to output `PFZ` category and a `Confidence` score."
    )

    st.markdown("#### Workflow")
    steps = ["Ocean Data (NetCDF)", "CCA Front Detection", "Feature Engineering",
              "Extra Trees Classifier", "PFZ Map + Archive"]
    cols = st.columns(len(steps) * 2 - 1)
    for i, step in enumerate(steps):
        with cols[i * 2]:
            st.markdown(
                f'<div class="pfz-card" style="text-align:center; font-size:0.85rem;">{step}</div>',
                unsafe_allow_html=True,
            )
        if i < len(steps) - 1:
            with cols[i * 2 + 1]:
                st.markdown(
                    '<div style="text-align:center; color:#8A93A0; padding-top:0.6rem;">→</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("#### Developers")
    st.markdown("Nithin V, Jyoshna")
    st.caption("Automated end-to-end via an Apache Airflow pipeline.")

with tab_settings:
    st.markdown("### Settings")

    st.markdown("#### Configured backend paths")
    st.caption("Read-only — sourced from config.py / Airflow Variables.")
    st.code(
        f"INPUT_PATH    = {INPUT_PATH}\n"
        f"OUTPUT_PATH   = {OUTPUT_PATH}\n"
        f"DATA_PATH     = {DATA_PATH}\n"
        f"MODEL_PATH    = {MODEL_PATH}\n"
        f"DATA_NC_PATH  = {DATA_NC_PATH}",
        language="text",
    )

    st.markdown("#### Session")
    if st.button("Clear cached session state"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session state cleared. Reload the page to reinitialize defaults.")

    st.markdown("#### About this build")
    st.caption("PFZ Classifier System dashboard · Streamlit multi-page app")
