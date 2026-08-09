from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from services.student_performance_service import get_performance, get_analytics
from services.student_ai_service import get_ai_recommendations
from services.student_dashboard_service import get_dashboard
from services.student_profile_service import get_profile
from services.student_subject_service import get_subjects
from services.student_marks_service import get_marks
from services.student_attendance_service import get_attendance
from services.student_career_service import get_career_recommendations
from services.student_certification_service import get_certifications
from services.student_project_service import get_projects
from services.student_feedback_service import save_feedback

student = Blueprint("student", __name__)

# ==============================
# Student Dashboard
# ==============================

@student.route("/student/dashboard")
def dashboard():

    reference_id = session.get("reference_id")

    data = get_dashboard(reference_id)

    return render_template(
        "student/dashboard.html",
        data=data
    )
@student.route("/student/profile")
def profile():

    reference_id = session.get("reference_id")

    data = get_profile(reference_id)

    return render_template(
        "student/profile.html",
        data=data
    )


@student.route("/student/subjects")
def subjects():

    reference_id = session.get("reference_id")

    subjects_data = get_subjects(reference_id)

    return render_template(
        "student/subjects.html",
        subjects=subjects_data
    )

# =========================================================
# MARKS
# =========================================================

@student.route("/student/marks")
def marks():

    reference_id = session.get("reference_id")

    marks_data = get_marks(reference_id)

    return render_template(
        "student/marks.html",
        marks=marks_data
    )


# =========================================================
# ATTENDANCE
# =========================================================

@student.route("/student/attendance")
def attendance():

    reference_id = session.get("reference_id")

    attendance_data = get_attendance(reference_id)

    return render_template(
        "student/attendance.html",
        attendance=attendance_data
    )


# =========================================================
# ACADEMIC PERFORMANCE
# =========================================================

@student.route("/student/performance")
def performance():

    reference_id = session.get("reference_id")

    data = get_performance(reference_id)

    return render_template(
        "student/performance.html",
        data=data
    )


# =========================================================
# PERFORMANCE ANALYTICS
# =========================================================

@student.route("/student/analytics")
def analytics():

    reference_id = session.get("reference_id")

    data = get_analytics(reference_id)

    return render_template(
        "student/analytics.html",
        data=data
    )


# =========================================================
# AI RECOMMENDATIONS
# =========================================================

@student.route("/student/ai-recommendations")
def ai_recommendations():

    reference_id = session.get("reference_id")

    data = get_ai_recommendations(reference_id)

    return render_template(
        "student/ai_recommendations.html",
        data=data
    )


# =========================================================
# CAREER
# =========================================================

@student.route("/student/career")
def career():

    reference_id = session.get("reference_id")

    data = get_career_recommendations(reference_id)

    return render_template(
        "student/career.html",
        data=data
    )


# =========================================================
# CERTIFICATIONS
# =========================================================

@student.route("/student/certifications")
def certifications():

    reference_id = session.get("reference_id")

    data = get_certifications(reference_id)

    return render_template(
        "student/certifications.html",
        data=data
    )


# =========================================================
# PROJECTS
# =========================================================

@student.route("/student/projects")
def projects():

    reference_id = session.get("reference_id")

    data = get_projects(reference_id)

    return render_template(
        "student/projects.html",
        data=data
    )


# =========================================================
# FEEDBACK
# =========================================================

@student.route(
    "/student/feedback",
    methods=["GET", "POST"]
)
def feedback():

    reference_id = session.get("reference_id")

    if request.method == "POST":

        success = save_feedback(
            reference_id,
            request.form
        )

        if success:

            flash(
                "Feedback submitted successfully.",
                "success"
            )

        else:

            flash(
                "Unable to submit feedback.",
                "danger"
            )

        return redirect(
            url_for("student.feedback")
        )

    return render_template(
        "student/feedback.html"
    )