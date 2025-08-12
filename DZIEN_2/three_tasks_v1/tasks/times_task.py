import pandas as pd
import numpy as np
from pathlib import Path

def solve_times(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    arr = df["time_min"].to_numpy(dtype=float)
    mean_time = float(np.mean(arr))
    median_time = float(np.median(arr))
    min_time = float(np.min(arr))
    max_time = float(np.max(arr))
    std_time = float(np.std(arr, ddof=0))
    z_scores = (arr - mean_time) / std_time if std_time > 0 else np.zeros_like(arr)
    best_indices = np.argsort(arr)[:5]
    best_five = arr[best_indices]
    return {
        "summary": {
            "mean": mean_time,
            "median": median_time,
            "min": min_time,
            "max": max_time,
            "std": std_time
        },
        "z_scores": z_scores,
        "best_five": best_five,
        "best_indices": best_indices
    }