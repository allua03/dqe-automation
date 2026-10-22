from typing import Optional

import pandas as pd
import psycopg2
from psycopg2.extensions import connection
from pandas import DataFrame


class PostgresConnectorContextManager:
    """
    PostgreSQL database context manager used by the DQ framework.

    Establishes a connection on `__enter__` and closes it on `__exit__`,
    exposing `get_data_sql` to run a query and return a pandas DataFrame.
    """

    def __init__(self, db_host: str, db_name: str, db_port, db_user: str, db_password: str,
                 autocommit: bool = False):
        self.db_host = db_host
        self.db_name = db_name
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.autocommit = autocommit
        self.connection: Optional[connection] = None

    def __enter__(self) -> "PostgresConnectorContextManager":
        self.connection = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )
        self.connection.autocommit = self.autocommit
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        if self.connection:
            self.connection.close()

    def get_connection(self) -> Optional[connection]:
        return self.connection

    def get_data_sql(self, sql: str) -> DataFrame:
        """Execute `sql` and return the result set as a DataFrame."""
        if self.connection is None:
            raise RuntimeError("Connection is not open. Use this class as a context manager.")
        return pd.read_sql_query(sql, self.connection)

