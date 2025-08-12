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
