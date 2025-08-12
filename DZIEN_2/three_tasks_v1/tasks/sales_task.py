from pathlib import Path
import pandas as pd

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
