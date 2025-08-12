import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

#ścieżki do plików
data_dir = Path("data")
sales_file = data_dir / "sales.csv"
marketing_file = data_dir / "marketing.xlsx"
currencies_file = data_dir / "currencies.json"

!pip install openpyxl

#wczytywanie danych
sales_df = pd.read_csv(sales_file,parse_dates=["date"])
marketing_df = pd.read_excel(marketing_file,parse_dates=["date"])
with open(currencies_file,"r",encoding="utf-8") as f:
    currencies_data = json.load(f)

#przygotowanie DataFrame z kursami walut
currencies_rows = []
for date_str,rates in currencies_data.items():
    currencies_rows.append({
        "date":pd.to_datetime(date_str),
        "USD":rates["USD"],
        "EUR":rates["EUR"]
    })
currencies_df = pd.DataFrame(currencies_rows)

#scalanie wszystkich danych
df = sales_df.merge(marketing_df,on=["date","country"],how="left")
df = df.merge(currencies_df,on="date",how="left")
df.head()


#kowersja sprzedaży na USD/EUR w zależności od kraju
def convert_sales(row):
    if row["country"] == "USA":
        return row["sales_pln"]/row["USD"],"USD"
    elif row["country"] == "Germany":
        return row["sales_pln"]/row["EUR"],"EUR"
    else:
        return row["sales_pln"],"PLN"
    
df[["sales_foreign","country"]] = df.apply(lambda r:pd.Series(convert_sales(r)),axis=1)

#Analiza NumPy: ROI(Return on Investment)
sales_arr = df["sales_pln"].to_numpy()
marketing_arr = df["marketing_spend_pln"].to_numpy()
roi_arr = (sales_arr - marketing_arr)/marketing_arr
df["ROI"] = np.round(roi_arr,2)

#wykres porównujący ROI
plt.figure(figsize=(8,5))
for country in df["country"].unique():
    subset = df[df["country"] == country]
    plt.plot(subset["date"],subset["ROI"],marker="o",label="country")

plt.title("ROI per country over time")
plt.xlabel("Date")
plt.ylabel("ROI")
plt.grid(True)
plt.legend(title="Country",loc="best")
plt.tight_layout()
plt.savefig("roi_plot.png")
plt.show()
