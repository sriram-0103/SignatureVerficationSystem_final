from flask import Blueprint
from flask import render_template

overview_bp = Blueprint(
    "overview",
    __name__
)


@overview_bp.route("/")
def overview():

    return render_template(
        "overview.html"
    )