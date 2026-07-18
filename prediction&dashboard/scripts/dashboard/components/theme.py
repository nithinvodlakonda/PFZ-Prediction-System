"""
Injects the shared theme.css once per page render.
Call inject_theme() near the top of every page, after set_page_config()
and initialize_session().
"""
from pathlib import Path
import streamlit as st

_CSS_PATH = Path(__file__).resolve().parent.parent / "style" / "theme.css"


def inject_theme():
    css = _CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def header_bar(title: str, subtitle: str = ""):
    """Small accent-bar header used on inner pages (Classifier, Trends, etc.)
    instead of the full gradient hero, which is reserved for Home only."""
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""<div class="pfz-header-bar"><h1>{title}</h1>{sub_html}</div>""",
        unsafe_allow_html=True,
    )
