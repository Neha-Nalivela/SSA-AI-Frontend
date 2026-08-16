from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for,
)

from services.auth_service import login as authenticate

auth = Blueprint("auth", __name__)


# =========================
# LOGIN PAGE
# =========================

@auth.route("/")
def login_page():
    return render_template("auth/login.html")


# =========================
# LOGIN
# =========================

@auth.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    user = authenticate(email, password)

    if user is None:
        flash("Invalid Email or Password", "danger")
        return redirect(url_for("auth.login_page"))

    session["user_id"] = user["UserID"]
    session["role"] = user["Role"]
    session["reference_id"] = user["ReferenceID"]

    if user["Role"] == "Admin":
        return redirect("/admin/dashboard")

    elif user["Role"] == "Faculty":
        return redirect("/faculty/dashboard")

    else:
        return redirect("/student/dashboard")


# =========================
# LOGOUT
# =========================

@auth.route("/logout", methods=["GET", "POST"])
def logout():

    # Clear all login/session information
    session.clear()

    # Show message on login page
    flash("You have been logged out successfully.", "success")

    # Redirect to the actual login PAGE
    return redirect(url_for("auth.login_page"))