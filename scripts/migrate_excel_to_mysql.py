"""Import every dataset registered by DataManager into MySQL.

Usage:
    python scripts/migrate_excel_to_mysql.py
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.mysql_manager import MySQLManager
from models.data_manager import DataManager


def main():
    if not MySQLManager.enabled():
        raise SystemExit("Set MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, and MYSQL_PASSWORD first.")

    DataManager.load_all()
    migrated = 0
    for dataset_name, dataframe in DataManager.datasets.items():
        if dataframe is None or dataframe.empty:
            continue
        filename = DataManager.dataset_filenames[dataset_name]
        MySQLManager.create_table_from_dataframe(filename, dataframe)
        migrated += 1
        print(f"Migrated {dataset_name} -> {MySQLManager.table_name(filename)} ({len(dataframe)} rows)")
    print(f"Migration complete: {migrated} dataset(s)")


if __name__ == "__main__":
    main()
