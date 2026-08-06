import sys
sys.path.append(r'D:/BTECH/All years/4-1/Project/Academic_AI')
from services.attainment_service import compute_co_attainment_for_subject, compute_po_attainment_for_subject
from models.data_manager import DataManager
DataManager.refresh()
print('Datasets:', list(DataManager.datasets.keys()))
subjects = DataManager.get('subjects')
if subjects is None or subjects.empty:
    print('No subjects')
else:
    subj = subjects.iloc[0]['SubjectID']
    ref = subjects.iloc[0].get('FacultyID', '')
    print('Testing subject', subj, 'faculty', ref)
    try:
        co = compute_co_attainment_for_subject(ref, subj)
        print('CO result:\n', co)
    except Exception as e:
        import traceback; traceback.print_exc()
    try:
        po = compute_po_attainment_for_subject(ref, subj)
        print('PO result:\n', po)
    except Exception as e:
        import traceback; traceback.print_exc()
