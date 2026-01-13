import pandas as pd
import plotly.express as px

def bar(df: pd.DataFrame, x: str, y: str, title: str):
    """
    Genera un bar chart Plotly
    """
    fig = px.bar(df, x=x, y=y, title=title)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


def line(df: pd.DataFrame, x: str, y: str, title: str):
    """
    Genera una línea Plotly
    """
    fig = px.line(df, x=x, y=y, title=title, markers=True)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


def box(df: pd.DataFrame, x: str, y: str, title: str):
    """
    Genera boxplot Plotly
    """
    fig = px.box(df, x=x, y=y, title=title, points="outliers")
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig
