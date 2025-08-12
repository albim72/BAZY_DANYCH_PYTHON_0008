from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def bar_mean_times(mean_times_by_race:pd.DataFrame, out_path:Path, add_labels:bool=True):
    # Wykres słupkowy (kolory opcjonalne — można usunąć jeśli niepożądane)
    thresholds = {"10K": 55, "Half": 125}
    colors = []
    for _, row in mean_times_by_race.iterrows():
        thr = thresholds.get(row["race"], np.inf)
        colors.append("green" if row["time_min"] < thr else "gray")

    plt.figure()
    plt.bar(mean_times_by_race["race"], mean_times_by_race["time_min"], color=colors)
    plt.title("Średnie czasy wg kategorii biegu")
    plt.xlabel("Kategoria biegu")
    plt.ylabel("Średni czas [min]")
    for i, v in enumerate(mean_times_by_race["time_min"]):
        plt.text(i, v + 1, f"{v:.1f}", ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
