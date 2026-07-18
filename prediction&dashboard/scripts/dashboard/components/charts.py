"""
Shared chart builders for Analytics and Trends pages. Kept as pure
functions returning Plotly figures, so pages stay thin and consistent.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.colors import CATEGORY_COLORS, CATEGORY_ORDER, TEAL, NAVY


def category_distribution_bar(df: pd.DataFrame, category_col: str = "PFZ"):
    counts = df[category_col].value_counts().reindex(CATEGORY_ORDER).fillna(0)
    fig = px.bar(
        x=counts.index, y=counts.values,
        color=counts.index, color_discrete_map=CATEGORY_COLORS,
        labels={"x": category_col, "y": "Pixel Count"},
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=320)
    return fig


def parameter_histogram(df: pd.DataFrame, column: str, title: str | None = None, color: str = TEAL):
    fig = px.histogram(df, x=column, nbins=40, color_discrete_sequence=[color])
    fig.update_layout(
        title=title or column,
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
        bargap=0.05,
    )
    return fig


def feature_importance_bar(fi_df: pd.DataFrame, feature_col: str, importance_col: str):
    plot_df = fi_df[[feature_col, importance_col]].sort_values(importance_col, ascending=True)
    fig = px.bar(
        plot_df, x=importance_col, y=feature_col, orientation="h",
        color_discrete_sequence=[NAVY],
    )
    fig.update_layout(
        title="Model Feature Importance",
        margin=dict(l=10, r=10, t=40, b=10),
        height=max(320, 24 * len(plot_df)),
    )
    return fig


def trend_line(df: pd.DataFrame, x_col: str, y_cols: list[str], title: str = ""):
    fig = go.Figure()
    palette = [NAVY, TEAL, "#fd7e14", "#28a745"]
    for i, y in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df[x_col], y=df[y], mode="lines+markers",
            name=y, line=dict(color=palette[i % len(palette)], width=2),
        ))
    fig.update_layout(
        title=title, margin=dict(l=10, r=10, t=40, b=10), height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def category_counts_over_time(archive_df: pd.DataFrame):
    """
    archive_df: one row per date with High/Medium/Low pixel counts.
    """
    fig = go.Figure()
    for cat in CATEGORY_ORDER:
        if cat in archive_df.columns:
            fig.add_trace(go.Scatter(
                x=archive_df["Date"], y=archive_df[cat],
                mode="lines+markers", name=cat,
                line=dict(color=CATEGORY_COLORS[cat], width=2),
                stackgroup=None,
            ))
    fig.update_layout(
        title="PFZ Category Counts Over Time",
        margin=dict(l=10, r=10, t=40, b=10), height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig
