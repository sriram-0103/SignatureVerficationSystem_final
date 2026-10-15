import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "signature_verification.db"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ai",
    "signature_forgery_model.pkl"
)

EXPORT_PATH = os.path.join(
    BASE_DIR,
    "exports"
)

os.makedirs(EXPORT_PATH, exist_ok=True)