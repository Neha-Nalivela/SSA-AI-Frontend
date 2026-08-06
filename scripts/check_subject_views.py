import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from services.faculty_subject_service import get_subject_dashboard, get_subject_internal_mark_students, get_subject_attendance_students
from models.data_manager import DataManager
DataManager.refresh()
subjects = DataManager.get('subjects')
subj = subjects.iloc[0]['SubjectID']
ref = subjects.iloc[0].get('FacultyID','')
print('subject', subj, 'ref', ref)
print('\nDashboard:')
print(get_subject_dashboard(ref, subj))
print('\nInternal students summary:')
subject, summary = get_subject_internal_mark_students(ref, subj)
print(subject['SubjectID'], summary.shape)
print(summary.head())
print('\nAttendance summary:')
subject, attend = get_subject_attendance_students(ref, subj)
print(subject['SubjectID'], attend.shape)
print(attend.head())
