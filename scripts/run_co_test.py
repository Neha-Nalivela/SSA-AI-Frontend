import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from services.attainment_service import compute_co_attainment_for_subject
from models.data_manager import DataManager
DataManager.refresh()
print('Calling with F004, SUB004')
print(compute_co_attainment_for_subject('F004','SUB004'))
from models.data_manager import DataManager
subjects = DataManager.get('subjects')
subjects = subjects.copy()
subjects['SubjectID'] = subjects['SubjectID'].astype(str).str.strip()
import re
subjects['_SubjectKey'] = subjects['SubjectID'].apply(lambda v: re.search(r"(\d+)", str(v)).group(1) if re.search(r"(\d+)", str(v)) else str(v).strip())
print('\nSubjects with keys for faculty F004:')
print(subjects[subjects['FacultyID']== 'F004'][['SubjectID','_SubjectKey','FacultyID']])
