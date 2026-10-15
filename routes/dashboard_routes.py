from flask import Blueprint
from flask import jsonify
from flask import render_template

from database.database import (
    get_dashboard_statistics
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html"
    )


@dashboard_bp.route("/dashboard_stats")
def dashboard_stats():

    return jsonify(

        get_dashboard_statistics()

    )