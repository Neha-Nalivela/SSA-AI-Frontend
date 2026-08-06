import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from models.data_manager import DataManager
DataManager.refresh()
qb = DataManager.get('question_bank')
marks = DataManager.get('marks')
print('question_bank columns:', list(qb.columns))
print('question_bank sample:\n', qb.head(3).to_dict(orient='records'))
print('\nmarks columns:', list(marks.columns))
print('marks sample:\n', marks.head(5).to_dict(orient='records'))
