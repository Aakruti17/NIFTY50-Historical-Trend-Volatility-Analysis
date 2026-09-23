import os
import mysql.connector
from src import config


conn = mysql.connector.connect(
    host=config.DB_CONFIG["host"],
    port=config.DB_CONFIG["port"],
    user=config.DB_CONFIG["user"],
    password=config.DB_CONFIG["password"],
)
cursor = conn.cursor()

sql_path = os.path.join(config.SQL_DIR, "01_create_tables.sql")
with open(sql_path, "r") as f:
    sql_script = f.read()

for statement in sql_script.split(";"):
    statement = statement.strip()
    if statement:
        cursor.execute(statement)

conn.commit()
cursor.close()
conn.close()
print("Database and tables created successfully!")