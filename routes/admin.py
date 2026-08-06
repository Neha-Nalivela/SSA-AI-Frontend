from flask import Blueprint, render_template
from services.dashboard_service import get_dashboard_summary

admin = Blueprint(
    "admin",
    __name__
)


@admin.route("/admin/dashboard")
def dashboard():
    data = get_dashboard_summary()
    return render_template(
        "admin/dashboard.html",
        data=data
    )