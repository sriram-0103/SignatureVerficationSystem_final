from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from core.signature_api import (
    upload_signature,
    get_signature,
    clear_signature
)

mobile_connected = False

signature_bp = Blueprint(
    "signature",
    __name__
)


@signature_bp.route("/signature-pad")
def signature_pad():

    return render_template(
        "mobile_signature.html"
    )

@signature_bp.route(
    "/signature/connect",
    methods=["POST"]
)
def connect():

    global mobile_connected

    mobile_connected = True

    return jsonify({
        "success": True
    })

@signature_bp.route("/signature/status")
def status():

    return jsonify({
        "connected": mobile_connected
    })

@signature_bp.route(
    "/signature/disconnect",
    methods=["POST"]
)
def disconnect():

    global mobile_connected

    mobile_connected = False

    return jsonify({
        "success": True
    })

@signature_bp.route(
    "/signature/upload",
    methods=["POST"]
)


def upload():

    data = request.get_json(silent=True) or {}

    signature = data.get("signature")

    if not isinstance(signature, list):
        return jsonify({
            "success": False,
            "message": "Invalid signature data."
        }), 400

    return jsonify(
        upload_signature(signature)
    )


@signature_bp.route("/signature/get")
def get():

    return jsonify(
        get_signature()
    )


@signature_bp.route(
    "/signature/clear",
    methods=["POST"]
)
def clear():

    return jsonify(
        clear_signature()
    )