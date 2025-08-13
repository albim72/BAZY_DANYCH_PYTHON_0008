import configparser
import mysql.connector

#ładowanie pliku konfiguracyjnego
config = configparser.ConfigParser()
config.read("config.ini")

#pobranie danych z sekcji [mysql]
db_user = config['mysql']['user']
db_password = config['mysql']['password']
db_host = config['mysql']['host']
db_port = config['mysql']['port']
db_database = config['mysql']['database']

connection = mysql.connector.connect(
    user = db_user,
    password = db_password,
    host = db_host,
    port = db_port,
    database = db_database
)

cursorObject = connection.cursor()
tabela_student = """
CREATE TABLE IF NOT EXISTS student(
firstname varchar(100),
lastname varchar(100),
studentid int primary key
);
"""

cursorObject.execute(tabela_student)

dodaj_studenta = """
INSERT INTO student(firstname,lastname,studentid) values(%s,%s,%s);
"""

val_one = ("Jan","Kot",65435)
cursorObject.execute(dodaj_studenta,val_one)

valmulti = [
    ("Maria","Kos",75423),
    ("Tomasz","Kłos",65666),
    ("Marek","Kloss",213134),
    ("Marian","Opinek",551445),
    ("Roma","Nowak",23341),
    ("Leon","Rom",651656),
    ("Mira","Kopik",2313646)
]

cursorObject.executemany(dodaj_studenta,valmulti)

connection.commit()
connection.close()
