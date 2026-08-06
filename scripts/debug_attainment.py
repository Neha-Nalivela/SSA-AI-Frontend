import sys, re
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from models.data_manager import DataManager
DataManager.refresh()
questions = DataManager.get('question_bank').copy()
marks = DataManager.get('marks').copy()
cos = DataManager.get('co').copy()
subjects = DataManager.get('subjects').copy()
students = DataManager.get('students').copy()
for df,name in [(questions,'questions'),(marks,'marks'),(cos,'cos'),(subjects,'subjects')]:
    print(name, df.shape)
# normalize
questions['SubjectID']=questions['SubjectID'].astype(str).str.strip()
marks['SubjectID']=marks['SubjectID'].astype(str).str.strip()
cos['SubjectID']=cos['SubjectID'].astype(str).str.strip()
subjects['SubjectID']=subjects['SubjectID'].astype(str).str.strip()
students['StudentID']=students['StudentID'].astype(str).str.strip()

from services.attainment_service import _numeric_key
questions['_SubjectKey']=questions['SubjectID'].apply(_numeric_key)
marks['_SubjectKey']=marks['SubjectID'].apply(_numeric_key)
cos['_SubjectKey']=cos['SubjectID'].apply(_numeric_key)
subjects['_SubjectKey']=subjects['SubjectID'].apply(_numeric_key)

subject_key = _numeric_key('SUB004')
reference_id = str('F004').strip()
print('subject_key',subject_key,'reference',reference_id)
print('subjects keys and faculty ids:')
print(subjects[['SubjectID','_SubjectKey','FacultyID']].head(20))
match = subjects[(subjects['_SubjectKey']==subject_key) & (subjects.get('FacultyID','')==reference_id)]
print('match rows:', match.shape)
print(match)
PY