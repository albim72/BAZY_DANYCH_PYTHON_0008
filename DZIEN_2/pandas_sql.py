from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path("shop.db")

def init_db(db_path: Path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS orders;
    
    CREATE TABLE customers
    (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        country TEXT NOT NULL
    );

    CREATE TABLE orders
    (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
        
        
    """)

    customers = [
        (1,"Anna Kowalska","PL"),
        (2,"John Smith","US"),
        (3,"Hans Muller","DE"),
        (4,"Karol Wiśniak","PL"),
        (5,"Marie Dubois","FR"),
        (6,"Natan Wote","GB"),
    ]

    orders = [
        (101,1,"2025-01-10",245.0),
        (102,1,"2025-01-11",356.0),
        (103,2,"2025-01-17",112.0),
        (104,3,"2025-01-12",1130.0),
        (105,4,"2025-01-13",789.0),
        (106,5,"2025-01-12",88.0),
        (107,5,"2025-01-18",321.0),
        (108,5,"2025-01-21",555.0),
        (109,1,"2025-01-22",975.0),
        (110,6,"2025-01-21",23.0),
        (111,6,"2025-01-27",450.0),
    ]

    cur.executemany("INSERT INTO customers VALUES (?,?,?)", customers)
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)

    conn.commit()
    return conn

def main():
    conn = init_db(DB_PATH)

    #proste SELECT
    df_customers = pd.read_sql_query("SELECT * FROM customers", conn)
    df_orders = pd.read_sql_query("SELECT * FROM orders", conn)

    print(f"\n[Customers]\n{df_customers}\n")
    print(f"\n[Orders]\n{df_orders}\n")

    #JOIN + GOUP BY
    q_join_agg = """
    SELECT
        c.country,
        COUNT(o.order_id) AS n_orders,
        ROUND(SUM(o.amount)) AS total_amount,
        ROUND(AVG(o.amount)) AS avg_amount
    FROM
        customers AS c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    GROUP BY c.country
    ORDER BY total_amount desc;
    """

    df_country_stats = pd.read_sql_query(q_join_agg, conn)
    print(f"\n[Country Stats]\n{df_country_stats}\n")
if __name__ == '__main__':
    main()
