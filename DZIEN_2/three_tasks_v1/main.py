from pathlib import Path

from tasks.sales_task import solve_sales
from tasks.times_task import solve_times
from tasks.races_task import solve_races


def main():
    base = Path(__file__).resolve().parent
    data_dir = base / "data"
    out = base / "output"
    out.mkdir(parents=True, exist_ok=True)

    # 1) Ścieżki do gotowych CSV
    sales_csv = data_dir / "sales.csv"
    times_csv = data_dir / "times_10k.csv"
    races_csv = data_dir / "races.csv"

    # 2) Uruchom zadania
    sales_result = solve_sales(sales_csv)
    times_result = solve_times(times_csv)
    races_result = solve_races(races_csv, out / "race_means.png")

    # Rozpakuj wyniki, NIE nadpisuj nazw stringami
    top3_customers = sales_result["top3_customers"]
    total_sales_per_customer = sales_result["total_sales_per_customer"]
    orders_per_category = sales_result["orders_per_category"]

    mean_times_by_race = races_result["mean_times_by_race"]          # DataFrame
    best_time_per_runner = races_result["best_time_per_runner"]      # DataFrame

    # 3) Wypisanie wyników
    print("[ZADANIE 1] TOP 3 klienci (sprzedaż łączna):")
    print(top3_customers.to_string(index=False))

    print("\n[ZADANIE 1] Sprzedaż łączna per klient (TOP 10):")
    print(total_sales_per_customer.head(10).to_string(index=False))

    print("\n[ZADANIE 1] Liczba zamówień per kategoria:")
    print(orders_per_category.to_string(index=False))

    print("\n[ZADANIE 2] Podsumowanie czasów 10K:")
    for k, v in times_result["summary"].items():
        print(f"  {k}: {v:.2f}")

    print("\n[ZADANIE 2] Najlepsze 5 czasów 10K (min):", times_result["best_five"])

    print("\n[ZADANIE 3] Średnie czasy wg kategorii:")
    print(mean_times_by_race.to_string(index=False))

    print("\n[ZADANIE 3] Najlepszy czas każdego zawodnika (top 10):")
    print(best_time_per_runner.head(10).to_string(index=False))

    print("\nWyniki i wykres zapisano w folderze:", out)


if __name__ == "__main__":
    main()
