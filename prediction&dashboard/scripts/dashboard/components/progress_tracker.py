"""
Live progress UI for run_pipeline.main(selected_date, progress_callback).
The pipeline calls progress_callback(step_message) after each of its
~22 sequential steps; this component turns that into a progress bar +
step list so the user can see exactly where the run is.
"""
import streamlit as st

from Utils.progress_steps import PIPELINE_STEPS

_TOTAL = len(PIPELINE_STEPS)


class ProgressTracker:
    """
    Usage:
        tracker = ProgressTracker()
        run_pipeline.main(selected_date, progress_callback=tracker.update)
    """

    def __init__(self):
        self._bar = st.progress(0, text="Waiting to start\u2026")
        self._status = st.empty()
        self._completed_steps: list[str] = []
        self._log_box = st.container()

    def update(self, step_message: str):
        if step_message in PIPELINE_STEPS:
            idx = PIPELINE_STEPS.index(step_message) + 1
        else:
            idx = len(self._completed_steps) + 1
        self._completed_steps.append(step_message)

        pct = min(idx / _TOTAL, 1.0)
        self._bar.progress(pct, text=f"Step {idx}/{_TOTAL} \u2014 {step_message}")

        with self._log_box:
            st.markdown(
                f'<span style="color:#0E7C86;">\u2713</span> {step_message}',
                unsafe_allow_html=True,
            )

    def finish(self):
        self._bar.progress(1.0, text="Prediction complete")
        self._status.success("Pipeline finished successfully.")
