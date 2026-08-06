import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
import pandas as pd
from models.data_manager import DataManager
from services.attainment_service import _numeric_key
DataManager.refresh()
questions = DataManager.get('question_bank').copy()
marks = DataManager.get('marks').copy()
cos = DataManager.get('co').copy()
subjects = DataManager.get('subjects').copy()
students = DataManager.get('students').copy()
for df,name in [(questions,'questions'),(marks,'marks'),(cos,'cos'),(subjects,'subjects')]:
    print(name, df.shape)
questions['SubjectID']=questions['SubjectID'].astype(str).str.strip()
marks['SubjectID']=marks['SubjectID'].astype(str).str.strip()
cos['SubjectID']=cos['SubjectID'].astype(str).str.strip()
subjects['SubjectID']=subjects['SubjectID'].astype(str).str.strip()
students['StudentID']=students['StudentID'].astype(str).str.strip()
questions['_SubjectKey']=questions['SubjectID'].apply(_numeric_key)
marks['_SubjectKey']=marks['SubjectID'].apply(_numeric_key)
cos['_SubjectKey']=cos['SubjectID'].apply(_numeric_key)
subjects['_SubjectKey']=subjects['SubjectID'].apply(_numeric_key)
subject_key=_numeric_key('SUB004')
reference_id='F004'
print('subject_key',subject_key)
match = subjects[(subjects['_SubjectKey']==subject_key) & (subjects.get('FacultyID','')==reference_id)]
print('match empty?', match.empty)
print('subj_questions count', len(questions[questions['_SubjectKey']==subject_key]))
print('subj_marks count', len(marks[marks['_SubjectKey']==subject_key]))
subj_questions = questions[questions['_SubjectKey']==subject_key]
subj_marks = marks[marks['_SubjectKey']==subject_key]
print('exam types in subj_marks:', subj_marks['ExamType'].unique())
# apply exam_types None, so no filter
# create q_meta
q_meta = subj_questions[['QuestionID','COID','MaxMarks']].copy()
q_meta['QuestionID']=q_meta['QuestionID'].astype(str).str.strip()
subj_marks = subj_marks.copy()
subj_marks['QuestionID']=subj_marks['QuestionID'].astype(str).str.strip()
print('merging counts before merge', subj_marks.shape, q_meta.shape)
merged = subj_marks.merge(q_meta, on='QuestionID', how='left', suffixes=('','_q'))
print('after merge', merged.shape)
print('rows with COID null', merged['COID'].isna().sum())
print('sample merged rows:')
print(merged.head(10))
