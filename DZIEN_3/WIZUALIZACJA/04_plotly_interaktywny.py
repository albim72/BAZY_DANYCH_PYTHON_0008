# -*- coding: utf-8 -*-
"""
ZADANIE: Plotly — interaktywny wykres
-------------------------------------
Zbuduj interaktywny wykres punktowy (scatter) pokazujący zależność tempa od tętna,
z animacją po tygodniach oraz dodatkowymi wymiarami (kolor=trasa, rozmiar=dystans).

Instrukcja:
    python 04_plotly_interaktywny.py
Wynik zapisze się jako HTML obok skryptu (możesz otworzyć w przeglądarce).
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px

def generate_dataset(seed: int = 202, days: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")
    routes = np.array(["Dolina", "Grzbiet", "Szczyt"])
    route = rng.choice(routes, size=days, p=[0.5, 0.3, 0.2])

    distance_km = rng.uniform(4, 20, size=days)
    base_pace = np.where(route == "Dolina", 5.6,
                  np.where(route == "Grzbiet", 6.3, 7.1))
    pace_min_per_km = base_pace + rng.normal(0, 0.35, size=days)
    avg_hr = 120 + (7.5 - pace_min_per_km) * 10 + rng.normal(0, 6, size=days)  # szybsze tempo -> wyższe HR

    df = pd.DataFrame({
        "date": dates,
        "week": dates.to_period("W").astype(str),
        "route": route,
        "distance_km": distance_km,
        "pace_min_per_km": pace_min_per_km,
        "avg_hr": avg_hr
    })
    return df

def main():
    df = generate_dataset()
    fig = px.scatter(
        df,
        x="avg_hr",
        y="pace_min_per_km",
        color="route",
        size="distance_km",
        animation_frame="week",
        hover_data={"date": True, "distance_km": True, "route": True},
        labels={
            "avg_hr": "Średnie tętno [bpm]",
            "pace_min_per_km": "Tempo [min/km]",
            "distance_km": "Dystans [km]",
            "route": "Trasa",
            "week": "Tydzień"
        },
        title="Tempo vs tętno z animacją po tygodniach (Plotly)"
    )
    fig.update_yaxes(autorange="reversed")  # mniejsze min/km jest „lepsze” — odwracamy oś

    out_html = "plotly_scatter_anim.html"
    fig.write_html(out_html, include_plotlyjs="cdn")
    print(f"[OK] Zapisano interaktywny wykres do: {out_html} (otwórz w przeglądarce).")

if __name__ == "__main__":
    main()
