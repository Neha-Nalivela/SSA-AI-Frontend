import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from models.data_manager import DataManager
DataManager.refresh()
qb = DataManager.get('question_bank')
print('total question rows', len(qb))
print('unique QuestionID count', qb['QuestionID'].nunique())
dups = qb[qb['QuestionID'].duplicated(keep=False)].sort_values('QuestionID')
print('duplicate count', len(dups))
print(dups.head(20).to_dict('records'))
