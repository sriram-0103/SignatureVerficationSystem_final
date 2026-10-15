"""
=========================================================
Signature Manager
Version : 1.0
Status  : LOCKED
=========================================================

This module is responsible only for temporarily storing
the current signature captured from the phone.

It does NOT:
- Access the database
- Run AI
- Register customers
- Verify signatures

It only manages signature transfer between
the mobile device and the laptop.
"""

from threading import Lock
from copy import deepcopy


class SignatureManager:

    def __init__(self):

        self._lock = Lock()

        self.clear()

    # ---------------------------------------------
    # Clear Current Signature
    # ---------------------------------------------

    def clear(self):

        with self._lock:

            self.signature = []

            self.updated = False

    # ---------------------------------------------
    # Save Signature
    # ---------------------------------------------

    def save(self, signature):

        with self._lock:

            self.signature = deepcopy(signature)

            self.updated = True

    # ---------------------------------------------
    # Read Signature
    # ---------------------------------------------

    def read(self):

        with self._lock:

            return deepcopy(self.signature)

    # ---------------------------------------------
    # Check Update
    # ---------------------------------------------

    def has_update(self):

        with self._lock:

            return self.updated

    # ---------------------------------------------
    # Reset Update Flag
    # ---------------------------------------------

    def reset(self):

        with self._lock:

            self.updated = False


signature_manager = SignatureManager()