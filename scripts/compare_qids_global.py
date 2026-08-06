import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from models.data_manager import DataManager
DataManager.refresh()
qb = DataManager.get('question_bank')
marks = DataManager.get('marks')
marks_s = marks[marks['SubjectID'].astype(str).str.contains('004')]
q_all = set(qb['QuestionID'].astype(str))
m_q = set(marks_s['QuestionID'].astype(str))
print('marks S004 count questions:', len(m_q))
print('question_bank all count questions:', len(q_all))
print('intersection global size', len(m_q & q_all))
print('intersection sample', list(m_q & q_all)[:50])
print('question_bank subjects for first 20 marks qids:')
for qid in list(m_q)[:20]:
    rows = qb[qb['QuestionID']==qid]
    if not rows.empty:
        print(qid, rows[['SubjectID','COID','BTL','Status']].to_dict('records'))
PY