from models.data_loader import load_excel


def get_students():
    return load_excel("06_Students.xlsx")


def get_faculty():
    return load_excel("05_Faculty.xlsx")


def get_users():
    return load_excel("23_Users.xlsx")