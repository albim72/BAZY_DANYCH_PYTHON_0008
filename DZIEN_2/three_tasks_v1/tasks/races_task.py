from utils.plotting import bar_mean_times
import pandas as pd
from pathlib import Path


def solve_races(csv_path: Path, plot_path: Path) -> dict:
    df = pd.read_csv(csv_path, parse_dates=["date"])
    mean_times_by_race = df.groupby("race", as_index=False)["time_min"].mean()
    best_time_per_runner = (
        df.groupby("name", as_index=False)["time_min"]
        .min()
        .rename(columns={"time_min":"best_time_min"})
        .sort_values("best_time_min")
    )
    bar_mean_times(mean_times_by_race, plot_path,add_labels=True)

    return {
        "mean_times_by_race": mean_times_by_race.sort_values("time_min"),
        "best_time_per_runner": best_time_per_runner
    }