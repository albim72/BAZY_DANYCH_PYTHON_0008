# -*- coding: utf-8 -*-
"""
ZADANIE: Wykresy w Pandas — analiza treningów biegowych
-------------------------------------------------------
Stwórz wykres pokazujący tygodniowy wolumen (suma km) oraz 7-dniową średnią kroczącą.
Dodatkowo wypisz tydzień z największym kilometrażem i zapisz wykres do pliku PNG.

Instrukcja:
    python 01_pandas_wykresy.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Konfiguracja katalogu na wykresy ---
PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

def generate_data(seed: int = 42, days: int = 120) -> pd.DataFrame:
    """Generuje syntetyczny dziennik treningowy (data, dystans_km, czas_min, trasa)."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")

    # Dystans zależny od dnia tygodnia (np. dłuższy bieg w weekend)
    weekday = dates.dayofweek.values
    base_km = rng.normal(7, 2, size=days).clip(0, None)
    weekend_boost = np.where(weekday >= 5, rng.normal(6, 1.5, size=days), 0)
    distance_km = (base_km + weekend_boost) * (rng.uniform(0.6, 1.2, size=days))

    pace_min_per_km = rng.normal(6.0, 0.4, size=days).clip(4.5, 7.5)  # min/km
    duration_min = distance_km * pace_min_per_km

    routes = np.array(["Dolina", "Grzbiet", "Szczyt"])
    route = rng.choice(routes, size=days, p=[0.5, 0.3, 0.2])

    df = pd.DataFrame({
        "date": dates,
        "distance_km": distance_km,
        "duration_min": duration_min,
        "route": route
    })
    return df

def main():
    df = generate_data()

    # Agregacja tygodniowa
    df = df.set_index("date").sort_index()
    weekly = df["distance_km"].resample("W-MON").sum().rename("weekly_km")
    rolling7 = df["distance_km"].rolling("7D").sum().rename("rolling_7d_km")

    # Wykres łączony (oś wspólna, dwie serie)
    fig, ax = plt.subplots(figsize=(10, 5))
    weekly.plot(ax=ax, kind="bar", alpha=0.7, label="Suma tygodniowa (km)")
    rolling7.plot(ax=ax, linestyle="-", marker="", label="Suma krocząca 7 dni (km)")

    ax.set_title("Wolumen biegania: tygodnie vs 7-dniowa suma krocząca")
    ax.set_xlabel("Tydzień (poniedziałek)")
    ax.set_ylabel("Kilometry")
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", linewidth=0.5)

    # Wypisanie najlepszego tygodnia
    best_week = weekly.idxmax()
    best_val = float(weekly.max())
    print(f"[INFO] Największy kilometraż tygodniowy: {best_val:.1f} km (tydzień zaczyna się {best_week.date()})")

    # Zapis
    out_path = os.path.join(PLOTS_DIR, "pandas_wolumen.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Wykres zapisano do: {out_path}")

if __name__ == "__main__":
    main()
