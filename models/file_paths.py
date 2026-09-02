import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_FOLDER = os.path.join(BASE_DIR, "data")
MASTER_FOLDER = os.path.join(DATA_FOLDER, "master")
OBE_FOLDER = os.path.join(DATA_FOLDER, "obe")
AI_FOLDER = os.path.join(DATA_FOLDER, "ai")
PROFILE_FOLDER = os.path.join(DATA_FOLDER, "profile")
STUDENTS = os.path.join(MASTER_FOLDER, "06_Students.xlsx")
FACULTY = os.path.join(MASTER_FOLDER, "05_Faculty.xlsx")
SUBJECTS = os.path.join(MASTER_FOLDER, "04_Subjects.xlsx")
USERS = os.path.join(MASTER_FOLDER, "23_Users.xlsx")
COURSES = os.path.join(MASTER_FOLDER, "01_Courses.xlsx")
FEEDBACK = os.path.join(MASTER_FOLDER, "22_Feedback.xlsx")
CO = os.path.join(OBE_FOLDER, "07_CO.xlsx")
PO = os.path.join(OBE_FOLDER, "08_PO.xlsx")
CO_PO = os.path.join(OBE_FOLDER, "09_CO_PO_Mapping.xlsx")
QUESTION_BANK = os.path.join(OBE_FOLDER, "10_Question_Bank.xlsx")