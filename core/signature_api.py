"""
=========================================================
Signature API
Version : 1.0
Status  : LOCKED
=========================================================
"""

from core.signature_manager import signature_manager


def upload_signature(signature):

    if not isinstance(signature, list):
        return {
            "success": False,
            "message": "Invalid signature data."
        }

    signature_manager.save(signature)

    return {
        "success": True
    }


def get_signature():

    return {

        "success": True,

        "updated": signature_manager.has_update(),

        "signature": signature_manager.read()

    }


def clear_signature():

    signature_manager.clear()

    return {

        "success": True

    }