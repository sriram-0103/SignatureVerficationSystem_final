from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import send_from_directory

from database.database import get_history

history_bp = Blueprint(
    "history",
    __name__
)


@history_bp.route("/history")
def history():

    return render_template(
        "history.html"
    )


@history_bp.route("/reports/<path:filename>")
def open_report(filename):

    return send_from_directory(
        "reports",
        filename
    )


@history_bp.route("/get_history")
def get_history_route():

    rows = get_history()

    history = []

    for row in rows:

        history.append({

            "verification_id": row["VerificationID"],

            "customer_name": row["Name"],

            "account_number": row["AccountNumber"],

            "decision": row["Decision"],

            "confidence": round(row["Confidence"], 2),

            "verification_time": row["VerificationTime"],

            "report_path": row["ReportPath"]

        })

    return jsonify(history)