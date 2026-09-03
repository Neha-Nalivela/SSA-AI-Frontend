from models.mysql_manager import MySQLManager


class FeedbackQuestionService:
    TABLE = "feedback_questions"
    RESPONSE_TABLE = "feedback_responses"
    DEFAULT_QUESTIONS = [
        "The faculty explains concepts clearly.",
        "The faculty encourages student participation.",
        "The faculty uses examples and practical applications.",
        "The faculty is regular and punctual.",
        "The faculty clarifies doubts effectively."
    ]

    @classmethod
    def _ensure_table(cls):
        with MySQLManager.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS `{cls.TABLE}` (
                    `QuestionID` INT AUTO_INCREMENT PRIMARY KEY,
                    `FacultyID` VARCHAR(100) NOT NULL,
                    `QuestionText` TEXT NOT NULL,
                    `QuestionType` VARCHAR(30) NOT NULL DEFAULT 'Rating',
                    `IsActive` TINYINT(1) NOT NULL DEFAULT 1,
                    `CreatedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS `{cls.RESPONSE_TABLE}` (
                    `ResponseID` INT AUTO_INCREMENT PRIMARY KEY,
                    `StudentID` VARCHAR(100) NOT NULL,
                    `SubjectID` VARCHAR(100) NOT NULL,
                    `QuestionID` INT NOT NULL,
                    `Answer` TEXT NOT NULL,
                    `CreatedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            try:
                cursor.execute(
                    f"ALTER TABLE `{cls.RESPONSE_TABLE}` ADD COLUMN `SubjectID` VARCHAR(100) NOT NULL DEFAULT ''"
                )
            except Exception:
                pass
            cursor.execute(f"SELECT COUNT(*) FROM `{cls.TABLE}`")
            if cursor.fetchone()[0] == 0:
                cursor.executemany(
                    f"INSERT INTO `{cls.TABLE}` (`FacultyID`, `QuestionText`, `QuestionType`) VALUES (%s, %s, %s)",
                    [("SYSTEM", text, "Rating") for text in cls.DEFAULT_QUESTIONS]
                )
            connection.commit()
            cursor.close()

    @classmethod
    def get_questions(cls, active_only=False):
        if not MySQLManager.enabled():
            return [
                {
                    "QuestionID": index,
                    "FacultyID": "SYSTEM",
                    "QuestionText": text,
                    "QuestionType": "Rating",
                    "IsActive": 1
                }
                for index, text in enumerate(cls.DEFAULT_QUESTIONS, start=1)
            ]

        try:
            cls._ensure_table()
            with MySQLManager.connection() as connection:
                cursor = connection.cursor(dictionary=True)
                query = f"SELECT * FROM `{cls.TABLE}`"
                if active_only:
                    query += " WHERE `IsActive` = 1"
                query += " ORDER BY `CreatedAt` DESC, `QuestionID` DESC"
                cursor.execute(query)
                questions = cursor.fetchall()
                cursor.close()
            return questions
        except Exception as error:
            print("Feedback question read error:", error)
            return []

    @classmethod
    def add_question(cls, faculty_id, question_text, question_type):
        if not MySQLManager.enabled():
            return False

        question_text = str(question_text or "").strip()
        question_type = str(question_type or "Rating").strip()
        if not question_text or question_type not in {"Rating", "Text"}:
            return False

        try:
            cls._ensure_table()
            with MySQLManager.connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f"INSERT INTO `{cls.TABLE}` (`FacultyID`, `QuestionText`, `QuestionType`) VALUES (%s, %s, %s)",
                    (str(faculty_id).strip(), question_text, question_type),
                )
                connection.commit()
                cursor.close()
            return True
        except Exception as error:
            print("Feedback question save error:", error)
            return False

    @classmethod
    def save_responses(cls, student_id, form, questions, subjects):
        if not MySQLManager.enabled() or not questions:
            return True

        answers = []
        for subject in subjects:
            subject_id = str(subject.get("SubjectID", "")).strip()
            for question in questions:
                field_name = f"Question_{subject_id}_{question['QuestionID']}"
                answer = str(form.get(field_name, "")).strip()
                if answer:
                    answers.append((str(student_id).strip(), subject_id, question["QuestionID"], answer))

        if not answers:
            return False

        try:
            cls._ensure_table()
            with MySQLManager.connection() as connection:
                cursor = connection.cursor()
                cursor.executemany(
                    f"INSERT INTO `{cls.RESPONSE_TABLE}` (`StudentID`, `SubjectID`, `QuestionID`, `Answer`) VALUES (%s, %s, %s, %s)",
                    answers,
                )
                connection.commit()
                cursor.close()
            return True
        except Exception as error:
            print("Feedback response save error:", error)
            return False
