import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from models.data_manager import DataManager
DataManager.refresh()
marks = DataManager.get('marks')
qb = DataManager.get('question_bank')
marks_s = marks[marks['SubjectID'].astype(str).str.contains('004')]
print('unique questionIDs in marks S004:', marks_s['QuestionID'].nunique())
print('unique questionIDs in qb S004:', qb[qb['SubjectID'].astype(str).str.contains('004')]['QuestionID'].nunique())
print('sorted marks qids sample 20:', sorted(list(marks_s['QuestionID'].unique()))[:20])
