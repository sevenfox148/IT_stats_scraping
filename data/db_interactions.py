import pandas as pd
from sqlalchemy import create_engine, exc, text
import pg8000
from os import environ
from logs.set_up_logger import get_logger

db_logger = get_logger("db_logger", "db_operations.log")


db_host = environ.get("DB_HOST")
db_port = environ.get("DB_PORT")
db_username = environ.get("DB_USERNAME")
db_password = environ.get("DB_PASSWORD")
db_name = environ.get("DB_NAME")

try:
    engine = create_engine(f"postgresql+pg8000://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}")
except exc.SQLAlchemyError as e:
    db_logger.error(f"Failed to connect to {db_host}/{db_name}: {e}")
    raise

def write_table(df, schema, table):
    try:
        with engine.connect() as connection:
            with connection.begin():
                added = df.to_sql(table, con=connection, if_exists='append', index=False, schema=schema)
                db_logger.info(f"Data successfully written to table {table}. Rows added: {added}")
                return added
    except exc.SQLAlchemyError as e:
        db_logger.error(f"Failed to write data to table {table}: {e}")
        raise

def read_table(schema, table, index=None):
    return pd.read_sql_table(table, engine, index_col=index, schema=schema)

def clear_table(schema, table):
    try:
        if not schema.isidentifier() or not table.isidentifier():
            db_logger.error(f"Invalid table name: {schema}.{table}")
            raise ValueError(f"ERROR: Invalid table name: {schema}.{table}")

        with engine.begin() as connection:
            query = text(f"TRUNCATE TABLE {schema}.{table}")
            connection.execute(query)
            db_logger.info(f"Table {schema}.{table} cleared.")

    except Exception as e:
        db_logger.error(f"Failed to clear table {schema}.{table}: {e}")
        raise