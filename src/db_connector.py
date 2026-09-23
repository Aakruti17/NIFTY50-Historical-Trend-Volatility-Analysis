import mysql.connector
from sqlalchemy import create_engine
import pandas as pd

from src import config

def get_mysql_connection():
    conn = mysql.connector.connect(
        host=config.DB_CONFIG["host"],
        port=config.DB_CONFIG["port"],
        user=config.DB_CONFIG["user"],
        password=config.DB_CONFIG["password"],
        database=config.DB_CONFIG["database"],
    )
    return conn


def get_sqlalchemy_engine():
    db = config.DB_CONFIG
    connection_string = (
        f"mysql+mysqlconnector://{db['user']}:{db['password']}"
        f"@{db['host']}:{db['port']}/{db['database']}"
    )
    engine = create_engine(connection_string)
    return engine


def run_sql_file(sql_file_path: str) -> None:
    with open(sql_file_path, "r") as f:
        sql_script = f.read()

    conn = get_mysql_connection()
    cursor = conn.cursor()
    for statement in sql_script.split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Executed SQL file: {sql_file_path}")


def push_dataframe_to_mysql(df: pd.DataFrame, table_name: str = config.TABLE_NAME,
                             if_exists: str = "replace") -> None:

    engine = get_sqlalchemy_engine()
    df.to_sql(table_name, con=engine, if_exists=if_exists, index=False, chunksize=1000)
    print(f"Uploaded {len(df)} rows into MySQL table '{table_name}'.")


def fetch_query(query: str) -> pd.DataFrame:
    """Run any SELECT query and get the result back as a pandas DataFrame."""
    engine = get_sqlalchemy_engine()
    return pd.read_sql(query, con=engine)


if __name__ == "__main__":
    try:
        conn = get_mysql_connection()
        print("Connected successfully! MySQL server info:", conn.get_server_info())
        conn.close()
    except mysql.connector.Error as err:
        print("Could not connect to MySQL:", err)
        print("Check your DB_CONFIG values in src/config.py or your environment variables.")
