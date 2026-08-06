import pandas as pd
def read_excel(file_path):
    return pd.read_excel(file_path)
def write_excel(df, file_path):
    df.to_excel(
        file_path,
        index=False
    )
def append_row(file_path, row):

    df = read_excel(file_path)

    df.loc[len(df)] = row

    write_excel(df, file_path)
def delete_row(
    file_path,
    column,
    value
):

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