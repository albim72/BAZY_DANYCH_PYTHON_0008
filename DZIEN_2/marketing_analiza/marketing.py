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
