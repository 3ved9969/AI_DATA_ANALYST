import os
import uuid
import plotly.express as px
import pandas as pd


def generate_chart(df: pd.DataFrame, chart_type: str, chart_folder: str) -> str | None:
    os.makedirs(chart_folder, exist_ok=True)

    if df.empty or len(df.columns) < 2 or chart_type in {"none", "table", None}:
        return None

    x_col = df.columns[0]
    y_col = df.columns[1]

    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")

        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")

        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col, title=f"{y_col} share by {x_col}")

        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")

        else:
            return None

        file_name = f"{uuid.uuid4().hex}.html"
        file_path = os.path.join(chart_folder, file_name)
        fig.write_html(file_path)

        return file_name

    except Exception:
        return None