from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from database.database import (
    get_template,
    get_customer_by_id,
    add_history
)

from ai.feature_extractor import FeatureExtractor
from ai.predictor import predict_signature
from reports.pdf_generator import generate_pdf

from datetime import datetime
import os


verification_bp = Blueprint(
    "verification",
    __name__
)

def calculate_similarity(reference, test):
    """
    Improved similarity calculation with feature weighting
    and tolerance for natural handwriting variation.
    """

    FEATURE_WEIGHTS = {
        # High importance
        "stroke_count": 3.0,
        "pen_lifts": 3.0,
        "duration": 2.5,
        "mean_velocity": 2.5,
        "mean_pressure": 2.5,
        "max_pressure": 2.0,

        # Medium importance
        "path_length": 2.0,
        "trajectory_complexity": 2.0,
        "direction_change_count": 2.0,
        "mean_curvature": 2.0,

        # Default weight
        "_default": 1.0
    }

    total_score = 0.0
    total_weight = 0.0

    for key, ref_value in reference.items():

        if key not in test:
            continue

        test_value = test[key]

        weight = FEATURE_WEIGHTS.get(
            key,
            FEATURE_WEIGHTS["_default"]
        )

        if abs(ref_value) < 1e-6:
            difference = abs(test_value)
        else:
            difference = abs(test_value - ref_value) / abs(ref_value)

        # Natural variation tolerance
        if difference <= 0.05:
            penalty = 0
        elif difference <= 0.10:
            penalty = 5
        elif difference <= 0.20:
            penalty = 15
        elif difference <= 0.35:
            penalty = 30
        else:
            penalty = 60

        score = max(0, 100 - penalty)

        total_score += score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    similarity = total_score / total_weight

    return round(similarity, 2)


@verification_bp.route("/verify")
def verify():

    return render_template(
        "verify.html"
    )


@verification_bp.route(
    "/verify_signature",
    methods=["POST"]
)
def verify_signature():

    try:

        data = request.get_json()

        template = get_template(
            data["customer_id"]
        )

        if template is None:

            return jsonify({

                "success": False,

                "message": "Template not found."

            })

        reference = template["FeatureVector"]

        customer = get_customer_by_id(
            data["customer_id"]
        )

        test = FeatureExtractor.extract(
            data["signature"]
        )

        ai_result = predict_signature(test)

        similarity = calculate_similarity(reference, test)

        ai_decision = ai_result["decision"]

        confidence = float(

            ai_result["confidence"]

        )

        HIGH_CONFIDENCE = 85
        MEDIUM_CONFIDENCE = 65

        if ai_decision == "Authentic":

            if confidence >= HIGH_CONFIDENCE:
                decision = "Authentic"

            elif confidence >= MEDIUM_CONFIDENCE:
                decision = "Human Verification Required"

            else:
                decision = "Forgery"

        else:  # AI predicted Forgery

            if confidence >= HIGH_CONFIDENCE:
                decision = "Forgery"

            elif confidence >= MEDIUM_CONFIDENCE:
                decision = "Human Verification Required"

            else:
                decision = "Authentic"

            pdf_name = (

            customer["AccountNumber"]

            + "_"

            + datetime.now().strftime(

                "%Y%m%d_%H%M%S"

            )

            + ".pdf"

        )

        pdf_path = os.path.join(

            "reports",

            pdf_name

        )

        generate_pdf(

            pdf_path,

            customer["Name"],

            customer["AccountNumber"],

            decision,

            ai_result["confidence"],

            similarity,

            reference,

            test

        )

        add_history(

            data["customer_id"],

            decision,

            ai_result["confidence"],

            pdf_path

        )

        return jsonify({

            "pdf": pdf_path,

            "success": True,

            "decision": decision,

            "confidence": ai_result["confidence"],

            "similarity": similarity,

            "reference_features": reference,

            "test_features": test

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        })