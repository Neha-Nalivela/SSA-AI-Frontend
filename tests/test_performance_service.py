import os
import tempfile
import unittest

from services import performance_service


class RemedialPlanTests(unittest.TestCase):
    def test_save_remedial_action_creates_excel_record(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_folder = performance_service.ACADEMIC_FOLDER
            performance_service.ACADEMIC_FOLDER = tmpdir
            try:
                saved = performance_service.save_remedial_action(
                    subject_id="S001",
                    student_id="ST1",
                    category="Weak",
                    remedial_classes="Extra class",
                    assessment="Quiz",
                    youtube_link="https://example.com",
                    notes="Need support"
                )
            finally:
                performance_service.ACADEMIC_FOLDER = original_folder

            self.assertEqual(saved["StudentID"], "ST1")
            self.assertEqual(saved["Category"], "Weak")
            self.assertEqual(saved["RemedialClasses"], "Extra class")
            self.assertEqual(saved["Assessment"], "Quiz")
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "18_RemedialClasses.xlsx")))


if __name__ == "__main__":
    unittest.main()
