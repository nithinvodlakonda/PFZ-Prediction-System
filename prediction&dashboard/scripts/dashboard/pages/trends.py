"""
Trends (new page) — turns the archive into an actual monitoring
dashboard: category counts over time, and rolling ocean-parameter
averages across days, powered by Utils.archive. Operates on
Front_Present == 1 pixels only, consistent with every other page.
"""
from datetime import datetime

import pandas as pd
import streamlit as st
import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(CURRENT_DIR)
SCRIPTS_DIR = os.path.dirname(DASHBOARD_DIR)

for path in [CURRENT_DIR, DASHBOARD_DIR, SCRIPTS_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)
from config import OUTPUT_PATH
from Utils.archive import get_prediction_archive
from Utils.output_loader import load_outputs
from components.data_prep import filter_front_present

from components.theme import header_bar
from components.charts import category_counts_over_time, trend_line

header_bar(
    "Trends",
    "Monitor how PFZ classifications and ocean parameters have evolved across archived runs.",
)

archive = get_prediction_archive(OUTPUT_PATH)

if not archive:
    st.info("No archived prediction runs yet — generate at least one on the Classifier page.")
    st.stop()

archive_dates = sorted(
    [datetime.strptime(a["Date"], "%Y-%m-%d").date() for a in archive]
)

col1, col2 = st.columns(2)
with col1:
    range_start = st.selectbox(
        "From", archive_dates, index=0, format_func=lambda d: d.isoformat(),
    )
with col2:
    range_end = st.selectbox(
        "To", archive_dates, index=len(archive_dates) - 1, format_func=lambda d: d.isoformat(),
    )

if range_start > range_end:
    st.error("The start date must be before the end date.")
    st.stop()

selected_dates = [d for d in archive_dates if range_start <= d <= range_end]
st.caption(f"Showing {len(selected_dates)} archived run(s) between {range_start} and {range_end}.")


@st.cache_data(show_spinner=False)
def _load_daily_stats(output_path: str, date_str: str):
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    outputs = load_outputs(output_path, d)
    raw_df = outputs.get("df")
    if raw_df is None or raw_df.empty:
        return None
    df = filter_front_present(raw_df)
    if df.empty:
        return None
    counts = df["PFZ"].value_counts()
    return {
        "Date": date_str,
        "High": int(counts.get("High", 0)),
        "Medium": int(counts.get("Medium", 0)),
        "Low": int(counts.get("Low", 0)),
        "avg_SST": df["SST"].mean() if "SST" in df else None,
        "avg_CHL": df["CHL"].mean() if "CHL" in df else None,
    }


rows = []
with st.spinner("Loading archived runs..."):
    for d in selected_dates:
        stats = _load_daily_stats(OUTPUT_PATH, d.isoformat())
        if stats:
            rows.append(stats)

if not rows:
    st.warning("Could not load any prediction files for the selected date range.")
    st.stop()

trend_df = pd.DataFrame(rows).sort_values("Date")

st.plotly_chart(category_counts_over_time(trend_df), use_container_width=True)

st.divider()
st.markdown("#### Ocean Parameter Trends")
avail_cols = [c for c in ["avg_SST", "avg_CHL"] if trend_df[c].notna().any()]
selected_metrics = st.multiselect(
    "Metrics to plot", avail_cols, default=avail_cols,
    format_func=lambda c: c.replace("avg_", "Average "),
)
if selected_metrics:
    st.plotly_chart(
        trend_line(trend_df, "Date", selected_metrics, title="Daily Averages"),
        use_container_width=True,
    )

st.divider()
st.markdown("#### Underlying Data")
st.dataframe(trend_df.reset_index(drop=True), use_container_width=True)
