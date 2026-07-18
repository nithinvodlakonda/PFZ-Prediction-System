"""
Reusable KPI metric row. Used on the Classifier page (above the map) and
on Analytics. Renders a row of pfz-kpi cards from a list of dicts, so the
same component can't drift out of sync with itself across pages.
"""
import streamlit as st


def render_kpi_row(kpis: list[dict], columns: int | None = None):
    """
    kpis: list of {"label": str, "value": str, "sub": str (optional)}
    columns: number of columns; defaults to len(kpis)
    """
    n = columns or len(kpis)
    cols = st.columns(n)
    for col, kpi in zip(cols, kpis):
        with col:
            sub_html = f'<div class="pfz-kpi-sub">{kpi["sub"]}</div>' if kpi.get("sub") else ""
            st.markdown(
                f"""
                <div class="pfz-kpi">
                    <div class="pfz-kpi-label">{kpi["label"]}</div>
                    <div class="pfz-kpi-value">{kpi["value"]}</div>
                    {sub_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
