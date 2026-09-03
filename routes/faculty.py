
from datetime import datetime, timedelta
import re

from flask import Blueprint
from flask import render_template
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from services.faculty_dashboard_service import get_dashboard
from models.data_manager import DataManager

from services.faculty_profile_service import (
    get_faculty_profile,
    update_faculty_profile
)

from services.question_bank_service import (
    get_all_questions,
    get_question,
    get_questions_by_subject,
    get_questions_for_faculty_subject,
    save_question,
    update_question,
    archive_question,
    delete_question
)
from services.faculty_subject_service import (
    get_faculty_subjects,
    get_subject_dashboard,
    get_subject_internal_mark_students,
    get_internal_marks_for_student,
    get_subject_external_mark_students,
    get_external_marks_for_student
)
# attendance helpers
from services.faculty_subject_service import (
    get_subject_attendance_students,
    get_attendance_for_student
)
from services.attainment_service import (
    compute_co_attainment_for_subject,
    compute_po_attainment_for_subject
)
from services.performance_service import (
    get_subject_performance_analysis,
    save_remedial_action,
)
from services.assessment_marks_service import AssessmentMarksService
from services.faculty_ai_service import get_faculty_ai_recommendations
from services.student_feedback_service import get_all_feedback, get_feedback_analytics
from services.feedback_question_service import FeedbackQuestionService

faculty = Blueprint(
    "faculty",
    __name__
)


@faculty.route("/faculty/dashboard")
def dashboard():

    reference_id = session.get("reference_id")

    data = get_dashboard(reference_id)

    return render_template(

        "faculty/dashboard.html",

        data=data

    )


@faculty.route("/faculty/feedback")
def feedback():

    feedback_data = get_all_feedback()

    return render_template(
        "faculty/feedback.html",
        feedback=feedback_data
    )


@faculty.route("/faculty/feedback/analytics")
def feedback_analytics():
    subject_id = request.args.get("subject_id", "").strip()
    return render_template(
        "faculty/feedback_analytics.html",
        analytics=get_feedback_analytics(subject_id),
        selected_subject=subject_id
    )


@faculty.route("/faculty/feedback/questions", methods=["GET", "POST"])
def feedback_questions():
    if request.method == "POST":
        saved = FeedbackQuestionService.add_question(
            session.get("reference_id"),
            request.form.get("QuestionText"),
            request.form.get("QuestionType")
        )
        flash(
            "Feedback question added successfully." if saved else "Unable to add feedback question.",
            "success" if saved else "danger"
        )
        return redirect(url_for("faculty.feedback_questions"))

    return render_template(
        "faculty/feedback_questions.html",
        questions=FeedbackQuestionService.get_questions()
    )


@faculty.route("/faculty/profile")
def profile():

    reference_id = session.get("reference_id")

    faculty_data = get_faculty_profile(reference_id)

    return render_template(

        "faculty/profile.html",

        faculty=faculty_data

    )


@faculty.route(
    "/faculty/profile/update",
    methods=["POST"]
)
def update_profile():

    reference_id = session.get("reference_id")

    update_faculty_profile(

        reference_id,

        request.form

    )

    flash(

        "Profile Updated Successfully.",

        "success"

    )

    return redirect(

        url_for("faculty.profile")

    )


@faculty.route("/faculty/subjects")
def subjects():

    reference_id = session.get("reference_id")

    subjects = get_faculty_subjects(reference_id)

    return render_template(

        "faculty/subjects/index.html",

        subjects=subjects

    )
@faculty.route("/faculty/question-bank")
def question_bank():

    questions = get_all_questions()

    return render_template(
        "faculty/question_bank/index.html",
        questions=questions
    )


@faculty.route("/faculty/subject/<subject_id>/question-bank")
def subject_question_bank(subject_id):
    reference_id = session.get("reference_id")

    questions = get_questions_for_faculty_subject(reference_id, subject_id)

    return render_template(
        "faculty/question_bank/index.html",
        questions=questions,
        subject_id=subject_id
    )
@faculty.route("/faculty/question-bank/add")
def add_question_page():

    return render_template(

        "faculty/question_bank/add.html"

    )


@faculty.route("/faculty/subject/<subject_id>/question-bank/add")
def add_question_page_subject(subject_id):

    return render_template(

        "faculty/question_bank/add.html",

        subject_id=subject_id

    )
@faculty.route(
    "/faculty/question-bank/save",
    methods=["POST"]
)
def save_question_route():

    success = save_question(

        request.form

    )

    if success:

        flash(

            "Question Added Successfully.",

            "success"

        )

    else:

        flash(

            "Question ID Already Exists.",

            "danger"

        )

    return redirect(

        url_for("faculty.question_bank")

    )
@faculty.route(
    "/faculty/question-bank/edit/<question_id>"
)
def edit_question(question_id):

    question = get_question(

        question_id

    )

    return render_template(

        "faculty/question_bank/edit.html",

        question=question

    )
@faculty.route(
    "/faculty/question-bank/update/<question_id>",
    methods=["POST"]
)
def update_question_route(question_id):

    update_question(

        question_id,

        request.form

    )

    flash(

        "Question Updated Successfully.",

        "success"

    )

    return redirect(

        url_for("faculty.question_bank")

    )
@faculty.route(
    "/faculty/question-bank/archive/<question_id>"
)
def archive_question_route(question_id):

    archive_question(

        question_id

    )

    flash(

        "Question Archived Successfully.",

        "warning"

    )

    return redirect(

        url_for("faculty.question_bank")

    )
@faculty.route(
    "/faculty/question-bank/delete/<question_id>"
)
def delete_question_route(question_id):

    delete_question(

        question_id

    )

    flash(

        "Question Deleted Successfully.",

        "danger"

    )

    return redirect(

        url_for("faculty.question_bank")

    )
@faculty.route("/faculty/question-bank/view/<question_id>")

@faculty.route("/faculty/subject/<subject_id>")
def subject_dashboard(subject_id):

    reference_id = session.get("reference_id")

    data = get_subject_dashboard(
        reference_id,
        subject_id
    )

    return render_template(

        "faculty/subjects/dashboard.html",

        data=data

    )


@faculty.route("/faculty/subject/<subject_id>/internal-marks")
def subject_internal_marks(subject_id):

    reference_id = session.get("reference_id")

    subject, student_summary = get_subject_internal_mark_students(
        reference_id,
        subject_id
    )

    student_rows = []
    mid1_total = 0
    mid2_total = 0
    average_total = 0
    student_count = 0

    if student_summary is not None and not student_summary.empty:
        student_rows = student_summary.to_dict(orient="records")
        student_count = len(student_rows)
        mid1_total = round(sum(float(r.get("Mid-1", 0)) for r in student_rows), 2)
        mid2_total = round(sum(float(r.get("Mid-2", 0)) for r in student_rows), 2)
        average_total = round((mid1_total + mid2_total) / 2, 2) if student_count else 0

    return render_template(
        "faculty/internal_marks.html",
        subject=subject,
        students=student_rows,
        student_count=student_count,
        mid1_total=mid1_total,
        mid2_total=mid2_total,
        average_total=average_total
    )


@faculty.route("/faculty/subject/<subject_id>/internal-marks/student/<student_id>")
def subject_internal_marks_student(subject_id, student_id):

    reference_id = session.get("reference_id")

    subject, student_marks = get_internal_marks_for_student(
        reference_id,
        subject_id,
        student_id
    )

    selected_exam = request.args.get("exam_type", "").strip()
    if selected_exam:
        student_marks = student_marks[student_marks["ExamType"] == selected_exam]

    return render_template(
        "faculty/internal_marks_student.html",
        subject=subject,
        student_marks=student_marks,
        student_id=student_id,
        external=False,
        selected_exam=selected_exam
    )


@faculty.route("/faculty/subject/<subject_id>/attendance")
def subject_attendance(subject_id):

    reference_id = session.get("reference_id")

    subject, student_summary = get_subject_attendance_students(
        reference_id,
        subject_id
    )

    student_rows = []
    student_count = 0
    total_sessions = 0

    if student_summary is not None and not student_summary.empty:
        student_rows = student_summary.to_dict(orient="records")
        student_count = len(student_rows)
        total_sessions = int(student_summary["Total"].max() if "Total" in student_summary.columns else 0)

    return render_template(
        "faculty/attendance.html",
        subject=subject,
        students=student_rows,
        student_count=student_count,
        total_sessions=total_sessions
    )


@faculty.route("/faculty/subject/<subject_id>/attendance/student/<student_id>")
def subject_attendance_student(subject_id, student_id):

    reference_id = session.get("reference_id")

    subject, records = get_attendance_for_student(
        reference_id,
        subject_id,
        student_id
    )

    detail_rows = []
    if records is not None and not records.empty:
        row = records.iloc[0]
        total = int(row.get("ClassesConducted", 0) or 0)
        attended = int(row.get("ClassesAttended", 0) or 0)
        base_date = row.get("Date") if "Date" in row.index else None
        if base_date is None:
            base_date = "2024-01-01"

        try:
            start_date = datetime.strptime(str(base_date), "%Y-%m-%d").date()
        except ValueError:
            start_date = datetime.strptime("2024-01-01", "%Y-%m-%d").date()

        for day in range(1, total + 1):
            current_date = start_date + timedelta(days=day - 1)
            detail_rows.append({
                "Date": current_date.strftime("%Y-%m-%d"),
                "Status": "Present" if day <= attended else "Absent"
            })

    return render_template(
        "faculty/attendance_student.html",
        subject=subject,
        records=records,
        detail_rows=detail_rows,
        student_id=student_id
    )



@faculty.route("/faculty/co-attainment")
def co_attainment_index():
    reference_id = session.get("reference_id")
    subjects = get_faculty_subjects(reference_id)
    return render_template(
        "faculty/co_attainment_index.html",
        subjects=subjects
    )


@faculty.route("/faculty/subject/<subject_id>/co-attainment")
def subject_co_attainment(subject_id):
    reference_id = session.get("reference_id")
    df = compute_co_attainment_for_subject(reference_id, subject_id)
    rows = df.to_dict(orient="records") if not df.empty else []
    return render_template(
        "faculty/co_attainment.html",
        subject_id=subject_id,
        rows=rows
    )


@faculty.route("/faculty/po-attainment")
def po_attainment_index():
    reference_id = session.get("reference_id")
    subjects = get_faculty_subjects(reference_id)
    return render_template(
        "faculty/po_attainment_index.html",
        subjects=subjects
    )


@faculty.route("/faculty/subject/<subject_id>/po-attainment")
def subject_po_attainment(subject_id):
    reference_id = session.get("reference_id")
    df = compute_po_attainment_for_subject(reference_id, subject_id)
    rows = df.to_dict(orient="records") if not df.empty else []
    return render_template(
        "faculty/po_attainment.html",
        subject_id=subject_id,
        rows=rows
    )


@faculty.route("/faculty/ai-recommendations")
def ai_recommendations():
    reference_id = session.get("reference_id")
    data = get_faculty_ai_recommendations(reference_id)
    return render_template(
        "faculty/ai_recommendations.html",
        data=data
    )


@faculty.route("/faculty/assessments")
def assessments():
    reference_id = session.get("reference_id")
    subjects = get_faculty_subjects(reference_id)
    return render_template(
        "faculty/assessments.html",
        subjects=subjects
    )


@faculty.route("/faculty/subject/<subject_id>/prepare-assessment", methods=["GET", "POST"])
def prepare_assessment(subject_id):
    faculty_id = str(session.get("reference_id", "")).strip()
    assigned = get_faculty_subjects(faculty_id)
    subject_rows = assigned[assigned["SubjectID"].astype(str).str.strip() == str(subject_id).strip()]
    if subject_rows.empty:
        flash("This subject is not assigned to your account.", "warning")
        return redirect(url_for("faculty.dashboard"))

    subject_key_match = re.search(r"(\d+)", str(subject_id))
    subject_key = subject_key_match.group(1) if subject_key_match else str(subject_id).strip()
    marks = DataManager.get("marks")
    student_ids = []
    if marks is not None and not marks.empty and {"SubjectID", "StudentID"}.issubset(marks.columns):
        mark_subject_keys = marks["SubjectID"].astype(str).str.extract(r"(\d+)", expand=False).fillna(
            marks["SubjectID"].astype(str).str.strip()
        )
        student_ids = sorted(
            marks.loc[mark_subject_keys == subject_key, "StudentID"]
            .astype(str).str.strip().unique().tolist()
        )

    students = DataManager.get("students")
    if students is not None and not students.empty and "StudentID" in students.columns:
        student_ids = sorted(students["StudentID"].astype(str).str.strip().unique().tolist())

    prepared = []
    if request.method == "POST":
        selected_student_ids = request.form.getlist("student_ids")
        topic = request.form.get("topic", "").strip() or None
        selected_student_ids = [student_id.strip() for student_id in selected_student_ids if student_id.strip()]
        invalid_ids = [student_id for student_id in selected_student_ids if student_id not in student_ids]
        if not selected_student_ids or invalid_ids:
            flash("Select one or more valid students.", "warning")
        else:
            prepared = [
                AssessmentMarksService.prepare_faculty_assessment(
                    faculty_id, student_id, subject_id
                    , topic=topic
                )
                for student_id in selected_student_ids
            ]
            prepared = [item for item in prepared if item]
            if prepared:
                flash(f"Assessment prepared for {len(prepared)} student(s).", "success")
            else:
                flash("No active questions are available for this subject.", "warning")

    return render_template(
        "faculty/prepare_assessment.html",
        subject=subject_rows.iloc[0],
        student_ids=student_ids,
        topics=AssessmentMarksService.get_subject_topics(subject_id),
        prepared=prepared,
    )


@faculty.route("/faculty/subject/<subject_id>/analytics", methods=["GET", "POST"])
def subject_performance_analysis(subject_id):
    reference_id = session.get("reference_id")
    subject, analysis = get_subject_performance_analysis(reference_id, subject_id)

    if subject is None:
        flash("Subject not found or not assigned to your account.", "warning")
        return redirect(url_for("faculty.dashboard"))

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        category = request.form.get("category", "").strip()
        remedial_classes = request.form.get("remedial_classes", "").strip()
        assessment = request.form.get("assessment", "").strip()
        youtube_link = request.form.get("youtube_link", "").strip()
        notes = request.form.get("notes", "").strip()

        if student_id and category:
            save_remedial_action(
                subject_id=subject_id,
                student_id=student_id,
                category=category,
                remedial_classes=remedial_classes,
                assessment=assessment,
                youtube_link=youtube_link,
                notes=notes,
            )
            flash("Remedial plan saved successfully.", "success")
        else:
            flash("Student and category are required.", "warning")

        subject, analysis = get_subject_performance_analysis(reference_id, subject_id)

    return render_template(
        "faculty/performance_analysis.html",
        subject=subject,
        analysis=analysis
    )


@faculty.route("/faculty/subject/<subject_id>/external-marks")
def subject_external_marks(subject_id):

    reference_id = session.get("reference_id")

    subject, student_summary = get_subject_external_mark_students(
        reference_id,
        subject_id
    )

    student_rows = []
    exam_label = "End Semester"
    student_count = 0
    exam_total = 0
    total_marks = 0

    if student_summary is not None and not student_summary.empty:
        student_rows = student_summary.to_dict(orient="records")
        student_count = len(student_rows)
        exam_total = round(sum(float(r.get(exam_label, 0)) for r in student_rows), 2)
        total_marks = round(sum(float(r.get("Total", 0)) for r in student_rows), 2)

    return render_template(
        "faculty/external_marks.html",
        subject=subject,
        students=student_rows,
        student_count=student_count,
        exam_label=exam_label,
        exam_total=exam_total,
        total_marks=total_marks
    )


@faculty.route("/faculty/subject/<subject_id>/external-marks/student/<student_id>")
def subject_external_marks_student(subject_id, student_id):

    reference_id = session.get("reference_id")

    subject, student_marks = get_external_marks_for_student(
        reference_id,
        subject_id,
        student_id
    )

    selected_exam = request.args.get("exam_type", "End Semester").strip()
    if selected_exam:
        student_marks = student_marks[student_marks["ExamType"] == selected_exam]

    return render_template(
        "faculty/internal_marks_student.html",
        subject=subject,
        student_marks=student_marks,
        student_id=student_id,
        external=True,
        selected_exam=selected_exam
    )
