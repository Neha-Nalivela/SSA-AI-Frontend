import os
import pandas as pd

from config import (
    MASTER_FOLDER,
    ACADEMIC_FOLDER,
    OBE_FOLDER,
    AI_FOLDER,
    PROFILE_FOLDER
)


class DataManager:

    datasets = {}

    @classmethod
    def load_dataset(cls, folder, filename):

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