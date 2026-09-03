import os
import re
from contextlib import contextmanager


class MySQLManager:
    """Small MySQL adapter used by the existing Excel-compatible data APIs."""

    @classmethod
    def enabled(cls):
        return bool(os.getenv("MYSQL_HOST"))

    @staticmethod
    def table_name(filename):
        name = os.path.splitext(os.path.basename(filename))[0]
        name = re.sub(r"^\d+_", "", name)
        return re.sub(r"[^a-zA-Z0-9_]", "_", name).lower()

    @classmethod
    @contextmanager
    def connection(cls):
        if not cls.enabled():
            raise RuntimeError("MySQL is not configured")
        import mysql.connector
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE"),
        )
        try:
            yield connection
        finally:
            connection.close()

    @classmethod
    def read_table(cls, filename):
        table = cls.table_name(filename)
        with cls.connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM `{table}`")
            rows = cursor.fetchall()
            cursor.close()
        return rows

    @classmethod
    def create_table_from_dataframe(cls, filename, dataframe):
        if dataframe is None or dataframe.empty:
            return
        table = cls.table_name(filename)
        columns = [str(column) for column in dataframe.columns]
        definitions = ", ".join(f"`{column}` TEXT NULL" for column in columns)
        with cls.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS `{table}` ({definitions})")
            cursor.close()
            connection.commit()
        cls.replace_table(filename, dataframe)

    @classmethod
    def replace_table(cls, filename, dataframe):
        table = cls.table_name(filename)
        columns = [str(column) for column in dataframe.columns]
        with cls.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM `{table}`")
            if columns and not dataframe.empty:
                names = ", ".join(f"`{column}`" for column in columns)
                placeholders = ", ".join(["%s"] * len(columns))
                query = f"INSERT INTO `{table}` ({names}) VALUES ({placeholders})"
                for values in dataframe.itertuples(index=False, name=None):
                    cursor.execute(query, tuple(None if str(value) == "nan" else value for value in values))
            cursor.close()
            connection.commit()

    @classmethod
    def append_row(cls, filename, row):
        table = cls.table_name(filename)
        columns = list(row.keys())
        names = ", ".join(f"`{column}`" for column in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        with cls.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO `{table}` ({names}) VALUES ({placeholders})",
                tuple(row[column] for column in columns),
            )
            connection.commit()
            cursor.close()

    @classmethod
    def update_row(cls, filename, column, value, updated_values):
        table = cls.table_name(filename)
        assignments = ", ".join(f"`{key}` = %s" for key in updated_values)
        parameters = list(updated_values.values()) + [value]
        with cls.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"UPDATE `{table}` SET {assignments} WHERE `{column}` = %s",
                parameters,
            )
            changed = cursor.rowcount > 0
            connection.commit()
            cursor.close()
        return changed

    @classmethod
    def delete_row(cls, filename, column, value):
        table = cls.table_name(filename)
        with cls.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM `{table}` WHERE `{column}` = %s", (value,))
            changed = cursor.rowcount > 0
            connection.commit()
            cursor.close()
        return changed
