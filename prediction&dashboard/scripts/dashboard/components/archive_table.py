"""
Renders the prediction archive (from Utils.archive.get_prediction_archive)
as a searchable, sortable table with per-row download buttons. Used on
the Downloads page. Replaces the old manual os.listdir() folder-walking.
"""
from pathlib import Path

import pandas as pd
import streamlit as st


def render_archive_table(archive: list[dict], output_path: str):
    if not archive:
        st.info("No archived predictions found yet.")
        return

    df = pd.DataFrame(archive)

    search = st.text_input(
        "Search archive by date (YYYY-MM-DD)",
        placeholder="e.g. 2026-06-15",
        key="archive_search",
    )
    if search:
        df = df[df["Date"].str.contains(search, case=False, na=False)]

    st.caption(f"{len(df)} of {len(archive)} archived prediction runs shown.")

    for _, row in df.iterrows():
        date = row["Date"]
        folder = Path(row["Folder"])
        csv_path = folder / f"pfz_prediction_{date}.csv"
        png_path = folder / f"PFZ_Output_{date}.png"
        nc_path = folder / f"PFZ_Output_{date}.nc"

        with st.container():
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            c1.markdown(f"**{date}**")
            _download_button(c2, "CSV", csv_path)
            _download_button(c3, "PNG", png_path)
            _download_button(c4, "NetCDF", nc_path)
            st.divider()


def _download_button(col, label: str, path: Path):
    if path.exists():
        with open(path, "rb") as f:
            col.download_button(
                label, f.read(), file_name=path.name,
                key=f"dl_{path.name}", use_container_width=True,
            )
    else:
        col.button(label, disabled=True, use_container_width=True, key=f"missing_{path}")
