import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from models.data_manager import DataManager
DataManager.refresh()
qb = DataManager.get('question_bank')
for qid in ['Q00025','Q00026','Q00027','Q00028','Q00029','Q00030','Q00031','Q00032']:
    rows=qb[qb['QuestionID']==qid]
    print(qid, rows[['SubjectID','COID','Subject']].to_dict('records'))
