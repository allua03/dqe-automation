
"""PostgreSQL connection and query support for DQ checks."""

from typing import Any, Optional

import pandas as pd
import psycopg2


class PostgresConnectorContextManager:
    """Manage a PostgreSQL connection and return query results as DataFrames."""

    def __init__(
        self,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
    ) -> None:
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.connection: Optional[Any] = None

    def __enter__(self) -> "PostgresConnectorContextManager":
        self.connection = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def get_data_sql(self, sql: str) -> pd.DataFrame:
        """Execute a read query on the active connection and return its rows."""
        if self.connection is None:
            raise RuntimeError("PostgreSQL connection is not open")
        return pd.read_sql_query(sql, self.connection)


