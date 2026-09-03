import pandas as pd
from models.mysql_manager import MySQLManager


def read_excel(file_path):
    if MySQLManager.enabled():
        try:
            return pd.DataFrame(MySQLManager.read_table(file_path))
        except Exception:
            pass
    return pd.read_excel(file_path)


def write_excel(df, file_path):
    if MySQLManager.enabled():
        try:
            MySQLManager.create_table_from_dataframe(file_path, df)
            return
        except Exception:
            pass
    df.to_excel(
        file_path,
        index=False
    )
def append_row(file_path, row):
    if MySQLManager.enabled():
        try:
            MySQLManager.append_row(file_path, row)
            return
        except Exception:
            pass

    df = read_excel(file_path)

    df.loc[len(df)] = row

    write_excel(df, file_path)
def delete_row(
    file_path,
    column,
    value
):
    if MySQLManager.enabled():
        try:
            MySQLManager.delete_row(file_path, column, value)
            return
        except Exception:
            pass

    df = read_excel(file_path)

    df = df[
        df[column] != value
    ]

    write_excel(df, file_path)
def update_row(
    file_path,
    column,
    value,
    updated_values
):
    if MySQLManager.enabled():
        try:
            return MySQLManager.update_row(file_path, column, value, updated_values)
        except Exception:
            pass

    df = read_excel(file_path)

    index = df[
        df[column] == value
    ].index

    if len(index) == 0:
        return False

    for key, val in updated_values.items():

        df.loc[index[0], key] = val

    write_excel(df, file_path)

    return True
def archive_row(
    file_path,
    column,
    value
):

    update_row(

        file_path,

        column,

        value,

        {

            "Status": "Archived"

        }

    )