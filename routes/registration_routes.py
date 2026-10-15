import sqlite3

from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from database.database import (
    add_customer,
    save_template,
    get_customer,
    get_template
)

from ai.feature_extractor import FeatureExtractor

registration_bp = Blueprint(
    "registration",
    __name__
)


@registration_bp.route("/register")
def register():

    return render_template(
        "register.html"
    )


@registration_bp.route(
    "/save_customer",
    methods=["POST"]
)
def save_customer():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received."
            })

        name = data.get("name", "").strip()

        account = data.get("account", "").strip()

        if not name or not account:

            return jsonify({
                "success": False,
                "message": "Name and Account Number are required."
            })

        reference1 = data.get("reference1")
        reference2 = data.get("reference2")
        reference3 = data.get("reference3")

        if not reference1 or not reference2 or not reference3:

            return jsonify({
                "success": False,
                "message": "Exactly three reference signatures are required."
            })

        try:

            customer_id = add_customer(
                name,
                account
            )

        except sqlite3.IntegrityError:

            return jsonify({
                "success": False,
                "message": "Account Number already exists."
            })

        feature1 = FeatureExtractor.extract(reference1)
        feature2 = FeatureExtractor.extract(reference2)
        feature3 = FeatureExtractor.extract(reference3)

        average = {}

        for key in feature1:

            average[key] = round(

                (
                    feature1[key] +
                    feature2[key] +
                    feature3[key]

                ) / 3,

                5

            )

        save_template(

            customer_id,

            reference1,

            reference2,

            reference3,

            average

        )

        return jsonify({

            "success": True,

            "customer_id": customer_id,

            "message": "Customer enrolled successfully."

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        })


@registration_bp.route(
    "/load_customer",
    methods=["POST"]
)
def load_customer():

    data = request.get_json()

    customer = get_customer(
        data["account"]
    )

    if customer is None:

        return jsonify({

            "success": False,

            "message": "Customer not found."

        })

    template = get_template(
        customer["CustomerID"]
    )

    if template is None:

        return jsonify({

            "success": False,

            "message": "Reference template not found."

        })

    return jsonify({

        "success": True,

        "customer_id": customer["CustomerID"],

        "name": customer["Name"],

        "account": customer["AccountNumber"],

        "feature_vector": template["FeatureVector"]

    })