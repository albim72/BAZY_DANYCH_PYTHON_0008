import pandas as pd
from sqlalchemy import create_engine

# Dane logowania do MySQL
MYSQL_USER = "root"
MYSQL_PASS = "abc123"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DB   = "bazatestowa"

# Tworzymy silnik SQLAlchemy
engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

# ----- ZAPIS -----
# Tworzymy mały DataFrame
df = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Aki", "Mika", "Ren"],
    "score": [88, 92, 79]
})

# Zapisujemy do MySQL
df.to_sql("simple_table", con=engine, if_exists="replace", index=False)

print("Tabela zapisana do MySQL.")

# ----- ODCZYT -----
# Wczytujemy tabelę z MySQL do DataFrame
df_read = pd.read_sql("SELECT * FROM simple_table", con=engine)
print("Odczytane dane:")
print(df_read)
