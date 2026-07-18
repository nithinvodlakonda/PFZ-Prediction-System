"""
REFERENCE IMPLEMENTATION — matches the documented contract exactly.
Your existing production Utils/session.py already does this; this file
exists only so the dashboard can be run and demoed standalone.
"""
import streamlit as st

_DEFAULTS = {
    "prediction_running": False,
    "prediction_completed": False,
    "prediction_df": None,
    "prediction_png": None,
    "prediction_csv": None,
    "prediction_nc": None,
    "runtime": None,
    "prediction_date": None,
}


def initialize_session():
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default
