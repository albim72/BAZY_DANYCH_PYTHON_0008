import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
from scipy import stats

# ==============================
# 1. KONFIGURACJA POŁĄCZENIA
# ==============================
MYSQL_USER = os.getenv("MYSQL_USER", "user")
MYSQL_PASS = os.getenv("MYSQL_PASS", "password")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB   = os.getenv("MYSQL_DB",   "demo_db")
TABLE_NAME = "products_demo"

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_engine(DATABASE_URL)

# ==============================
# 2. ODCZYT TABELI DO PANDAS
# ==============================
with engine.connect() as conn:
    df = pd.read_sql(text(f"SELECT * FROM {TABLE_NAME}"), conn)

print(f"Załadowano {len(df)} rekordów z tabeli {TABLE_NAME}.")
print(df.head())

# ==============================
# 3. ANALIZA Z PANDAS + NUMPY
# ==============================

# Podstawowe statystyki sprzedaży
print("\n--- Statystyki ilości i ceny ---")
print(df[['quantity', 'unit_price', 'revenue_est']].describe())

# NumPy: wylicz medianę i odchylenie standardowe przychodów
revenues = df['revenue_est'].to_numpy()
print(f"\nMediana przychodów: {np.median(revenues):.2f}")
print(f"Odchylenie standardowe przychodów: {np.std(revenues, ddof=1):.2f}")

# NumPy: znajdź top 5 rekordów po przychodach
top5_idx = np.argsort(revenues)[-5:][::-1]
print("\n--- TOP 5 po przychodach ---")
print(df.iloc[top5_idx])

# ==============================
# 4. ANALIZA ZE SCIPY (TEST STATYSTYCZNY)
# ==============================

# Porównanie średniej ceny pomiędzy dwoma kategoriami
cat1 = "valves"
cat2 = "pumps"
prices_cat1 = df.loc[df['category'] == cat1, 'unit_price']
prices_cat2 = df.loc[df['category'] == cat2, 'unit_price']

# Test t-Studenta dla dwóch niezależnych prób
t_stat, p_value = stats.ttest_ind(prices_cat1, prices_cat2, equal_var=False)

print(f"\n--- Test t-Studenta: {cat1} vs {cat2} ---")
print(f"T-stat: {t_stat:.3f}, p-value: {p_value:.5f}")
if p_value < 0.05:
    print("Wniosek: Różnice w średnich cenach są statystycznie istotne (α=0.05).")
else:
    print("Wniosek: Brak istotnych różnic w średnich cenach (α=0.05).")

# ==============================
# 5. WYKRES W MATPLOTLIB
# ==============================

# Suma przychodów w każdej kategorii
revenue_by_cat = df.groupby('category')['revenue_est'].sum().sort_values(ascending=False)

plt.figure(figsize=(8, 5))
bars = plt.bar(revenue_by_cat.index, revenue_by_cat.values, color='skyblue', edgecolor='black')
plt.title("Łączne przychody według kategorii")
plt.xlabel("Kategoria")
plt.ylabel("Przychód [PLN]")
plt.xticks(rotation=45)

# Dodaj wartości nad słupkami
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height, f"{height:,.0f}", 
             ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()
