import pandas as pd
import os
from config import MASTER_FOLDER


def load_excel(filename):
    path = os.path.join(MASTER_FOLDER, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"{filename} not found")

    return pd.read_excel(path)