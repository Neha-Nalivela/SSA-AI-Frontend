from flask import Flask

from config import SECRET_KEY

from models.data_manager import DataManager

from routes.auth import auth
from routes.admin import admin
from routes.faculty import faculty
from routes.student import student

from routes.student_admin import student_admin
from routes.faculty_admin import faculty_admin
from routes.subject_admin import subject_admin
from routes.co_admin import co_admin
from routes.po_admin import po_admin
from routes.co_po_admin import co_po_admin
from routes.question_bank_admin import question_bank_admin


app = Flask(__name__)

app.secret_key = SECRET_KEY

DataManager.load_all()

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(faculty)
app.register_blueprint(student)

app.register_blueprint(student_admin)
app.register_blueprint(faculty_admin)
app.register_blueprint(subject_admin)
app.register_blueprint(co_admin)
app.register_blueprint(po_admin)
app.register_blueprint(co_po_admin)
app.register_blueprint(question_bank_admin)


if __name__ == "__main__":
    app.run(debug=True)