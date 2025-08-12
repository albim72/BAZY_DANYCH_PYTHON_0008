import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

#ścieżki do plików
data_dir = Path("data")
sales_file = data_dir / "sales.csv"
marketing_file = data_dir / "markieting.xlsx"
currencies_file = data_dir / "currencies.json"

#wczytywanie danych
sales_df = pd.read_csv(sales_file,parse_dates=["date"])
marketing_df = pd.read_excel(marketing_file,parse_dates=["date"])
with open(currencies_file,"r",encoding="utf-8") as f:
    currencies_data = json.load(f)
