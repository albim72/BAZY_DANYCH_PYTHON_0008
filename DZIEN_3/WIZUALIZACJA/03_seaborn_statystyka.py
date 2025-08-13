# -*- coding: utf-8 -*-
"""
ZADANIE: Seaborn — estetyczne wizualizacje statystyczne
------------------------------------------------------
Porównaj rozkłady tempa (min/km) dla trzech typów tras: Dolina, Grzbiet, Szczyt.
Zastosuj wykres skrzypcowy (violin) z dodaną medianą (linia) i punktami (strip).

Instrukcja:
    python 03_seaborn_statystyka.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

def generate_runs(seed: int = 123, n: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    routes = np.array(["Dolina", "Grzbiet", "Szczyt"])
    route = rng.choice(routes, size=n, p=[0.45, 0.35, 0.20])

    # Tempa różnią się w zależności od trudności trasy
    base = {
        "Dolina": (5.6, 0.35),
        "Grzbiet": (6.2, 0.4),
        "Szczyt": (7.0, 0.5),
    }
    pace = np.zeros(n)
    for i, r in enumerate(route):
        mu, sigma = base[r]
        pace[i] = rng.normal(mu, sigma)
    pace = pace.clip(4.5, 8.5)

    return pd.DataFrame({"route": route, "pace_min_per_km": pace})

def main():
    df = generate_runs()

    sns.set_theme()  # przyjemne domyślne style
    fig, ax = plt.subplots(figsize=(9, 5))

    sns.violinplot(
        data=df, x="route", y="pace_min_per_km",
        inner=None, cut=0, ax=ax
    )
    sns.stripplot(
        data=df, x="route", y="pace_min_per_km",
        size=2.5, alpha=0.5, ax=ax
    )
    sns.pointplot(
        data=df, x="route", y="pace_min_per_km",
        estimator="median", errorbar=None, join=False, ax=ax
    )

    ax.set_title("Rozkłady tempa wg typu trasy (Seaborn)")
    ax.set_xlabel("Trasa")
    ax.set_ylabel("Tempo [min/km]")
    ax.grid(True, axis="y", linestyle="--", linewidth=0.5)

    out_path = os.path.join(PLOTS_DIR, "seaborn_tempa.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Wykres zapisano do: {out_path}")

if __name__ == "__main__":
    main()
