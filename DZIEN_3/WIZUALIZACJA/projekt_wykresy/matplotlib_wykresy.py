# -*- coding: utf-8 -*-
"""
ZADANIE: Matplotlib — baza do tworzenia wykresów
-----------------------------------------------
Wizualizuj zależność tętna od przewyższenia dla syntetycznych podbiegów.
Dodaj:
 - linię trendu (prosta regresji)
 - adnotacje dla 3 najbardziej stromych podbiegów
 - zapis do pliku PNG

Instrukcja:
    python 02_matplotlib_baza.py
"""

import os
import numpy as np
import matplotlib.pyplot as plt

PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

def generate_hill_repeats(seed: int = 7, n: int = 120):
    rng = np.random.default_rng(seed)
    elevation_gain = rng.normal(120, 40, size=n).clip(30, 300)  # m
    avg_hr = 120 + 0.25 * elevation_gain + rng.normal(0, 8, size=n)  # bpm zależne od przewyższenia
    return elevation_gain, avg_hr

def main():
    x, y = generate_hill_repeats()
    fig, ax = plt.subplots(figsize=(9, 5))

    # Scatter
    ax.scatter(x, y, alpha=0.75)
    ax.set_title("Podbiegi: tętno a przewyższenie (syntetyczne)")
    ax.set_xlabel("Przewyższenie pojedynczego podbiegu [m]")
    ax.set_ylabel("Średnie tętno [bpm]")
    ax.grid(True, linestyle="--", linewidth=0.5)

    # Linia trendu (regresja liniowa)
    coef = np.polyfit(x, y, deg=1)
    xp = np.linspace(x.min(), x.max(), 100)
    yp = np.polyval(coef, xp)
    ax.plot(xp, yp, linewidth=2, label=f"Trend: y = {coef[0]:.2f}x + {coef[1]:.1f}")
    ax.legend()

    # Adnotacje dla 3 najbardziej stromych (największe x)
    idx_sorted = np.argsort(-x)[:3]
    for i in idx_sorted:
        ax.annotate(f"#{i} ({x[i]:.0f} m)",
                    xy=(x[i], y[i]),
                    xytext=(5, 5),
                    textcoords="offset points")

    out_path = os.path.join(PLOTS_DIR, "matplotlib_podbiegi.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Wykres zapisano do: {out_path}")

if __name__ == "__main__":
    main()