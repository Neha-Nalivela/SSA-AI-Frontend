import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from models.data_manager import DataManager
DataManager.refresh()
qb = DataManager.get('question_bank')
marks = DataManager.get('marks')
q_q = set(qb[qb['SubjectID'].astype(str).str.contains('004')]['QuestionID'].astype(str))
m_q = set(marks[marks['SubjectID'].astype(str).str.contains('004')]['QuestionID'].astype(str))
print('question_bank question ids sample 10:', list(q_q)[:10])
print('marks question ids sample 10:', list(m_q)[:10])
print('intersection size', len(q_q & m_q))
print('some differences (marks not in qb) sample 10:', list(m_q - q_q)[:20])
