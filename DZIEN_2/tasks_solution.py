#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zadania: wersja z zewnętrznymi plikami CSV (po 300 rekordów).
Tworzy dane, zapisuje do CSV, wczytuje i rozwiązuje zadania, generuje wykres.

Wymagania:
    - Python 3.9+
    - numpy, pandas, matplotlib

Uruchomienie (np.):
    python tasks_solution.py

Pliki wyjściowe:
    - sales.csv
    - times_10k.csv
    - races.csv
    - race_means.png
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import random
from pathlib import Path


def make_sales_csv(path: Path, n: int = 300, seed: int = 42) -> Path:
    rng = np.random.default_rng(seed)
    customers = [
        "Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kamiński", "Lewandowski",
        "Zieliński", "Szymański", "Woźniak", "Dąbrowski", "Kozłowski", "Jankowski",
        "Mazur", "Krawczyk", "Kaczmarek", "Piotrowski", "Grabowski", "Zając",
        "Pawłowski", "Michalski"
    ]
    categories = ["electronics", "books", "home", "fashion", "sports", "toys", "beauty"]

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 8, 1)
    date_range_days = (end_date - start_date).days

    order_ids = [f"ORD{100000+i}" for i in range(n)]
    sales_df = pd.DataFrame({
        "order_id": order_ids,
        "customer": rng.choice(customers, size=n),
        "category": rng.choice(categories, size=n, p=[0.25,0.15,0.15,0.15,0.1,0.1,0.1]),
        "amount": np.round(rng.gamma(shape=2.0, scale=150.0, size=n) + rng.normal(0, 20, n), 2),
        "order_date": [
            (start_date + timedelta(days=int(rng.integers(0, date_range_days)))).strftime("%Y-%m-%d")
            for _ in range(n)
        ]
    })
    # Bez wartości ujemnych po dodanym szumie
    sales_df["amount"] = sales_df["amount"].clip(lower=5.0)
    out = path / "sales.csv"
    sales_df.to_csv(out, index=False)
    return out


def solve_sales(csv_path: Path) -> dict:
    sales = pd.read_csv(csv_path, parse_dates=["order_date"])
    electronics_only = sales[sales["category"] == "electronics"].copy()
    sales["amount_with_vat"] = (sales["amount"] * 1.23).round(2)
    total_sales_per_customer = (
        sales.groupby("customer", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount":"total_sales"})
        .sort_values("total_sales", ascending=False)
    )
    orders_per_category = (
        sales.groupby("category", as_index=False)["order_id"]
        .count()
        .rename(columns={"order_id":"orders_count"})
        .sort_values("orders_count", ascending=False)
    )
    top3_customers = total_sales_per_customer.head(3).copy()
    return {
        "electronics_only": electronics_only,
        "total_sales_per_customer": total_sales_per_customer,
        "orders_per_category": orders_per_category,
        "top3_customers": top3_customers
    }


def make_times_csv(path: Path, n: int = 300, seed: int = 42) -> Path:
    rng = np.random.default_rng(seed)
    times = rng.normal(loc=50, scale=5, size=n)
    times = np.clip(times, 35, 75)
    times_df = pd.DataFrame({
        "runner_id": [f"R{str(i+1).zfill(3)}" for i in range(n)],
        "time_min": np.round(times, 2)
    })
    out = path / "times_10k.csv"
    times_df.to_csv(out, index=False)
    return out


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


def make_races_csv(path: Path, n: int = 300, seed: int = 42) -> Path:
    rng = np.random.default_rng(seed)
    random.seed(seed)
    names_pool = [
        "Anna", "Piotr", "Kasia", "Marek", "Ewa", "Tomek", "Magda", "Paweł", "Agnieszka", "Krzysztof",
        "Monika", "Rafał", "Ola", "Michał", "Dorota", "Bartek", "Karolina", "Łukasz", "Natalia", "Adam",
        "Justyna", "Sebastian", "Iwona", "Damian", "Beata", "Grzegorz", "Patrycja", "Hubert", "Eliza", "Wojtek"
    ]
    race_types = ["10K", "Half"]

    def random_date(start, end, _rng):
        days = int((end - start).days)
        return (start + timedelta(days=int(_rng.integers(0, days)))).strftime("%Y-%m-%d")

    rows = []
    for _ in range(n):
        name = random.choice(names_pool)
        race = random.choice(race_types)
        if race == "10K":
            t = np.clip(rng.normal(50, 6), 34, 80)
        else:
            t = np.clip(rng.normal(120, 12), 80, 200)
        date_str = random_date(datetime(2025,1,1), datetime(2025,8,1), rng)
        rows.append({"name": name, "race": race, "time_min": round(float(t), 2), "date": date_str})

    races_df = pd.DataFrame(rows)
    out = path / "races.csv"
    races_df.to_csv(out, index=False)
    return out


def solve_races(csv_path: Path, plot_path: Path) -> dict:
    df = pd.read_csv(csv_path, parse_dates=["date"])
    mean_times_by_race = df.groupby("race", as_index=False)["time_min"].mean()
    best_time_per_runner = (
        df.groupby("name", as_index=False)["time_min"]
        .min()
        .rename(columns={"time_min":"best_time_min"})
        .sort_values("best_time_min")
    )

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

    return {
        "mean_times_by_race": mean_times_by_race.sort_values("time_min"),
        "best_time_per_runner": best_time_per_runner
    }


def main():
    base = Path(".").resolve()
    out_dir = base

    # 1) Dane sprzedażowe
    sales_csv = make_sales_csv(out_dir, n=300, seed=42)
    sales_result = solve_sales(sales_csv)

    # 2) Czas 10K
    times_csv = make_times_csv(out_dir, n=300, seed=42)
    times_result = solve_times(times_csv)

    # 3) Wyniki biegów
    races_csv = make_races_csv(out_dir, n=300, seed=42)
    race_plot = out_dir / "race_means.png"
    races_result = solve_races(races_csv, race_plot)

    # Prosta prezentacja wyników w konsoli
    print("\\n[ZADANIE 1] TOP 3 klienci (sprzedaż łączna):")
    print(sales_result["top3_customers"].to_string(index=False))

    print("\\n[ZADANIE 2] Podsumowanie czasów 10K:")
    for k, v in times_result["summary"].items():
        print(f"  {k}: {v:.2f}")

    print("\\n[ZADANIE 2] Najlepsze 5 czasów 10K (min):", np.round(times_result["best_five"], 2))

    print("\\n[ZADANIE 3] Średnie czasy wg kategorii:")
    print(races_result["mean_times_by_race"].to_string(index=False))

    print("\\n[ZADANIE 3] Najlepszy czas każdego zawodnika (top 10):")
    print(races_result["best_time_per_runner"].head(10).to_string(index=False))

    print("\\nPliki zapisane w:", out_dir)


if __name__ == "__main__":
    main()
