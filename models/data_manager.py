import os
import pandas as pd
from models.mysql_manager import MySQLManager

from config import (
    MASTER_FOLDER,
    ACADEMIC_FOLDER,
    OBE_FOLDER,
    AI_FOLDER,
    PROFILE_FOLDER
)


class DataManager:

    datasets = {}
    dataset_filenames = {
        "courses": "01_Courses.xlsx",
        "departments": "02_Departments.xlsx",
        "semesters": "03_Semesters.xlsx",
        "subjects": "04_Subjects.xlsx",
        "faculty": "05_Faculty.xlsx",
        "students": "06_Students.xlsx",
        "co": "07_CO.xlsx",
        "po": "08_PO.xlsx",
        "co_po": "09_CO_PO_Mapping.xlsx",
        "question_bank": "10_QuestionBank.xlsx",
        "marks": "11_StudentMarks.xlsx",
        "attendance": "12_Attendance.xlsx",
        "skills": "13_Skills.xlsx",
        "interests": "14_Interests.xlsx",
        "resources": "15_Resources.xlsx",
        "career": "16_CareerMapping.xlsx",
        "feedback": "17_Feedback.xlsx",
        "remedial": "18_RemedialClasses.xlsx",
        "placement": "19_PlacementReadiness.xlsx",
        "projects": "20_StudentProjects.xlsx",
        "certifications": "21_StudentCertifications.xlsx",
        "recommendations": "22_StudentRecommendations.xlsx",
        "users": "23_Users.xlsx",
        "assessments": "24_AssessmentMarks.xlsx",
        "weekly_reports": "25_WeeklyAssessmentReports.xlsx",
    }

    @classmethod
    def load_dataset(cls, folder, filename):

        if MySQLManager.enabled():
            try:
                rows = MySQLManager.read_table(filename)
                return pd.DataFrame(rows)
            except Exception as error:
                print(f"MySQL table unavailable for {filename}: {error}")

        path = os.path.join(folder, filename)

        if os.path.exists(path):
            return pd.read_excel(path)

        print(f"{filename} not found")

        return pd.DataFrame()

    @classmethod
    def load_all(cls):
        cls.datasets = {
            # MASTER
            "courses":
                cls.load_dataset(MASTER_FOLDER,
                                 "01_Courses.xlsx"),
            "departments":
                cls.load_dataset(MASTER_FOLDER,
                                 "02_Departments.xlsx"),
            "semesters":
                cls.load_dataset(MASTER_FOLDER,
                                 "03_Semesters.xlsx"),
            "subjects":
                cls.load_dataset(MASTER_FOLDER,
                                 "04_Subjects.xlsx"),
            "faculty":
                cls.load_dataset(MASTER_FOLDER,
                                 "05_Faculty.xlsx"),
            "students":
                cls.load_dataset(MASTER_FOLDER,
                                 "06_Students.xlsx"),
            "users":
                cls.load_dataset(MASTER_FOLDER,
                                 "23_Users.xlsx"),
            # ACADEMIC
            "marks":
                cls.load_dataset(ACADEMIC_FOLDER,
                                 "11_StudentMarks.xlsx"),
            "attendance":
                cls.load_dataset(ACADEMIC_FOLDER,
                                 "12_Attendance.xlsx"),
            "skills":
                cls.load_dataset(ACADEMIC_FOLDER,
                                 "13_Skills.xlsx"),
            "interests":
                cls.load_dataset(ACADEMIC_FOLDER,
                                 "14_Interests.xlsx"),
            "assessments":
                cls.load_dataset(ACADEMIC_FOLDER,"24_AssessmentMarks.xlsx"),
            "weekly_reports":
                cls.load_dataset(ACADEMIC_FOLDER,"25_WeeklyAssessmentReports.xlsx"),
            # OBE
            "co":
                cls.load_dataset(OBE_FOLDER,
                                 "07_CO.xlsx"),
            "po":
                cls.load_dataset(OBE_FOLDER,
                                 "08_PO.xlsx"),
            "co_po":
                cls.load_dataset(OBE_FOLDER,
                                 "09_CO_PO_Mapping.xlsx"),
            "question_bank":
                cls.load_dataset(OBE_FOLDER,
                                 "10_QuestionBank.xlsx"),
            # AI
            "resources":
                cls.load_dataset(AI_FOLDER,
                                 "15_Resources.xlsx"),
            "career":
                cls.load_dataset(AI_FOLDER,
                                 "16_CareerMapping.xlsx"),
            "feedback":
                cls.load_dataset(AI_FOLDER,
                                 "17_Feedback.xlsx"),
            "remedial":
                cls.load_dataset(AI_FOLDER,
                                 "18_RemedialClasses.xlsx"),
            "placement":
                cls.load_dataset(AI_FOLDER,
                                 "19_PlacementReadiness.xlsx"),
            "recommendations":
                cls.load_dataset(PROFILE_FOLDER,
                                 "22_StudentRecommendations.xlsx"),
            # PROFILE
            "projects":
                cls.load_dataset(PROFILE_FOLDER,
                                 "20_StudentProjects.xlsx"),
            "certifications":
                cls.load_dataset(PROFILE_FOLDER,
                                 "21_StudentCertifications.xlsx")
        }

    @classmethod
    def get(cls, name):
        return cls.datasets.get(name)
    
    @classmethod
    def refresh(cls):
        cls.load_all()