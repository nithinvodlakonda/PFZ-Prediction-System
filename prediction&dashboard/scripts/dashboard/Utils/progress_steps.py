"""
Single source of truth for the pipeline's ~22 step names, so run_pipeline.py
and the dashboard's progress UI never drift out of sync with each other.
"""

PIPELINE_STEPS = [
    "Validate Input Files", "Load Ocean Datasets", "Create Prediction Grid",
    "Remove Land Pixels", "Run CCA Front Detection", "Extract Chlorophyll",
    "Extract Front Features", "Filter Candidate Pixels", "Extract Bathymetry",
    "Extract Ocean Currents", "Extract Wind", "Extract Sea Surface Salinity",
    "Extract Ekman Transport", "Extract Sea Surface Temperature",
    "Extract Distance to Coast", "Extract Eddy Features", "Feature Engineering",
    "Save Feature Dataset", "Run Machine Learning Prediction",
    "Save Prediction CSV", "Generate NetCDF Output", "Generate PFZ Map",
]
