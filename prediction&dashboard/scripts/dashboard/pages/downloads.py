"""
Downloads — rebuilt using Utils.archive.get_prediction_archive() instead
of manual os.listdir() folder-walking (old build duplicated this logic
badly across pages).
"""
import streamlit as st

from config import OUTPUT_PATH
from Utils.archive import get_prediction_archive

from components.theme import header_bar
from components.archive_table import render_archive_table

header_bar("Downloads", "Browse and download every archived PFZ prediction run.")

archive = get_prediction_archive(OUTPUT_PATH)
render_archive_table(archive, OUTPUT_PATH)
