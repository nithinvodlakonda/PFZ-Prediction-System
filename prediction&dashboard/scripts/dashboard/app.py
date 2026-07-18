"""
PFZ Classifier System — entry point / page router.

Uses Streamlit's st.navigation()/st.Page() API so page titles, icons and
order are controlled explicitly in one place, rather than relying on
filename-prefix ordering in a bare pages/ folder.

set_page_config() and initialize_session() are called exactly ONCE here,
since this script re-runs on every navigation (before the selected
page's script executes) — individual page files must NOT call either
of these again.
"""
import streamlit as st

st.set_page_config(
    page_title="PFZ Classifier System",
    page_icon="assets/incois_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

from Utils.session import initialize_session  # noqa: E402
initialize_session()

from components.theme import inject_theme  # noqa: E402
inject_theme()

pages = [
    st.Page("pages/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("pages/classifier.py", title="Classifier", icon=":material/travel_explore:"),
    st.Page("pages/trends.py", title="Trends", icon=":material/trending_up:"),
    st.Page("pages/analytics.py", title="Analytics", icon=":material/analytics:"),
    st.Page("pages/downloads.py", title="Downloads", icon=":material/download:"),
]

with st.sidebar:
    st.image("assets/incois_logo.png", width=72)
    st.markdown("**PFZ Classifier System**")
    st.caption("INCOIS · Ocean Data Management")
    st.divider()

nav = st.navigation(pages)
nav.run()
