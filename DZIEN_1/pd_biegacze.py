import pandas as pd
import matplotlib.pyplot as plt

# --- Dane ---
races = {
    "name": ["Ewa", "Marcin", "Anna", "Tomek", "Ewa", "Marcin", "Anna"],
    "race": ["10K", "10K", "10K", "10K", "Half", "Half", "Half"],
    "time_min": [52, 49, 55, 60, 120, 115, 130],
    "date": pd.to_datetime(["2025-06-01", "2025-06-01", "2025-06-01", "2025-06-01",
                             "2025-07-15", "2025-07-15", "2025-07-15"])
}
df = pd.DataFrame(races)

# --- 1. Średni czas per bieg i dystans ---
avg_times = df.groupby("race")["time_min"].mean()

# --- 2. Najlepsze czasy każdej osoby ---
best_times = df.groupby("name")["time_min"].min()

# --- 3. Filtrowanie po progu czasowym (Half < 125 min) ---
half_fast = df[(df["race"] == "Half") & (df["time_min"] < 125)]

# --- 4. Wykres średnich czasów ---
avg_times.plot(kind="bar", title="Średni czas w minutach", ylabel="min", xlabel="Dystans")
plt.tight_layout()
plt.show()

print("\nŚrednie czasy:\n", avg_times)
print("\nNajlepsze czasy zawodników:\n", best_times)
print("\nSzybsi w półmaratonie:\n", half_fast)
