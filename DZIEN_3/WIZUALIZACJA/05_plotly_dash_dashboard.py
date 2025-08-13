# -*- coding: utf-8 -*-
"""
ZADANIE: Plotly Dash — interaktywny dashboard
---------------------------------------------
Zbuduj prosty dashboard z:
 - rozwijaną listą wyboru trasy,
 - wykresem szeregu czasowego tempa (min/km) i 7-dniowej średniej,
 - histogramem rozkładu tempa dla wybranej trasy.

Instrukcja uruchomienia:
    python 05_plotly_dash_dashboard.py
Następnie otwórz adres wypisany w konsoli (np. http://127.0.0.1:8050).
"""

import numpy as np
import pandas as pd

from datetime import timedelta
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

def generate(seed: int = 77, days: int = 150) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")
    routes = np.array(["Dolina", "Grzbiet", "Szczyt"])
    route = rng.choice(routes, size=days, p=[0.5, 0.3, 0.2])

    distance_km = rng.uniform(5, 18, size=days)
    base_pace = np.where(route == "Dolina", 5.7,
                  np.where(route == "Grzbiet", 6.4, 7.2))
    pace = (base_pace + rng.normal(0, 0.35, size=days)).clip(4.5, 8.5)
    df = pd.DataFrame({"date": dates, "route": route, "distance_km": distance_km, "pace_min_per_km": pace})
    return df

df = generate()
df = df.sort_values("date")

app = Dash(__name__)
app.title = "Dashboard biegowy"

app.layout = html.Div([
    html.H2("Dashboard biegowy — Plotly Dash"),
    html.P("Wybierz trasę, aby zobaczyć szczegóły tempa i rozkładu."),
    dcc.Dropdown(
        id="route-dd",
        options=[{"label": r, "value": r} for r in sorted(df["route"].unique())] + [{"label": "Wszystkie", "value": "ALL"}],
        value="ALL",
        clearable=False
    ),
    dcc.Graph(id="ts-graph"),
    dcc.Graph(id="hist-graph"),
])

@app.callback(
    Output("ts-graph", "figure"),
    Output("hist-graph", "figure"),
    Input("route-dd", "value")
)
def update_figs(route):
    dff = df if route == "ALL" else df[df["route"] == route]

    # Szereg czasowy + 7-dniowa średnia ruchoma
    dff2 = dff.set_index("date").copy()
    dff2["rolling_7d"] = dff2["pace_min_per_km"].rolling("7D").mean()

    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=dff2.index, y=dff2["pace_min_per_km"],
        mode="lines+markers", name="Tempo [min/km]"
    ))
    fig_ts.add_trace(go.Scatter(
        x=dff2.index, y=dff2["rolling_7d"],
        mode="lines", name="Średnia krocząca 7 dni"
    ))
    fig_ts.update_layout(
        title="Tempo w czasie (z 7-dniową średnią)",
        xaxis_title="Data",
        yaxis_title="Tempo [min/km]",
        yaxis=dict(autorange="reversed")  # mniejsze tempo = lepiej
    )

    # Histogram tempa
    fig_hist = px.histogram(
        dff,
        x="pace_min_per_km",
        nbins=30,
        title="Rozkład tempa [min/km]"
    )

    return fig_ts, fig_hist

if __name__ == "__main__":
    app.run_server(debug=True)
