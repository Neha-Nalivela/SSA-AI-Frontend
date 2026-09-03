from models.mysql_manager import MySQLManager


class FeedbackQuestionService:
    TABLE = "feedback_questions"

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
            connection.commit()
            cursor.close()

    @classmethod
    def get_questions(cls, active_only=False):
        if not MySQLManager.enabled():
            return []

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
