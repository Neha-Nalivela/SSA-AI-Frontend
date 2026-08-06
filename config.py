import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_FOLDER = os.path.join(BASE_DIR, "data")

MASTER_FOLDER = os.path.join(DATA_FOLDER, "master")
ACADEMIC_FOLDER = os.path.join(DATA_FOLDER, "academic")
OBE_FOLDER = os.path.join(DATA_FOLDER, "obe")
AI_FOLDER = os.path.join(DATA_FOLDER, "ai")
PROFILE_FOLDER = os.path.join(DATA_FOLDER, "profile")

SECRET_KEY = "academic_ai_secret_key"