import os
import joblib
import pandas as pd

# -----------------------------
# Load AI Model Once
# -----------------------------

ROOT = os.path.dirname(os.path.dirname(__file__))

MODEL_PATH = os.path.join(
    ROOT,
    "signature_forgery_model_v2.pkl"
)

FEATURE_PATH = os.path.join(
    ROOT,
    "feature_names_v2.pkl"
)

model = joblib.load(MODEL_PATH)

FEATURE_ORDER = joblib.load(FEATURE_PATH)


def predict_signature(features):

    df = pd.DataFrame(

        [[features[name] for name in FEATURE_ORDER]],

        columns=FEATURE_ORDER

    )

    prediction = int(

        model.predict(df)[0]

    )

    probabilities = model.predict_proba(df)[0]

    confidence = round(

        max(probabilities) * 100,

        2

    )

    decision = (

        "Authentic"

        if prediction == 1

        else "Forgery"

    )

    return {

        "prediction": prediction,

        "decision": decision,

        "confidence": confidence

    }