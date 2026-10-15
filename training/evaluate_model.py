import json
import joblib
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report
)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading model...")

model = joblib.load(
    "signature_forgery_model_v2.pkl"
)

X_test = np.load(
    "X_test.npy"
)

y_test = np.load(
    "y_test.npy"
)

print("Model Loaded")
print("Test Samples :", len(X_test))


# ============================================================
# PREDICTION
# ============================================================

prediction = model.predict(X_test)

probability = model.predict_proba(X_test)[:, 1]


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    prediction
)

precision = precision_score(
    y_test,
    prediction,
    zero_division=0
)

recall = recall_score(
    y_test,
    prediction,
    zero_division=0
)

f1 = f1_score(
    y_test,
    prediction,
    zero_division=0
)

roc = roc_auc_score(
    y_test,
    probability
)

print("\nAccuracy :", round(accuracy * 100, 2), "%")
print("Precision:", round(precision * 100, 2), "%")
print("Recall   :", round(recall * 100, 2), "%")
print("F1 Score :", round(f1 * 100, 2), "%")
print("ROC AUC  :", round(roc, 4))

print("\nClassification Report\n")

print(
    classification_report(
        y_test,
        prediction
    )
)

# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    prediction
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm
)

disp.plot()

plt.tight_layout()

plt.savefig(
    "confusion_matrix.png",
    dpi=300
)

plt.close()

# ============================================================
# ROC CURVE
# ============================================================

fpr, tpr, _ = roc_curve(
    y_test,
    probability
)

plt.figure(figsize=(6,6))

plt.plot(
    fpr,
    tpr,
    label=f"AUC = {roc:.4f}"
)

plt.plot(
    [0,1],
    [0,1],
    "--"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")

plt.legend()

plt.tight_layout()

plt.savefig(
    "roc_curve.png",
    dpi=300
)

plt.close()


# ============================================================
# PRECISION RECALL CURVE
# ============================================================

precision_curve, recall_curve, _ = precision_recall_curve(
    y_test,
    probability
)

plt.figure(figsize=(6,6))

plt.plot(
    recall_curve,
    precision_curve
)

plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision Recall Curve")

plt.tight_layout()

plt.savefig(
    "precision_recall_curve.png",
    dpi=300
)

plt.close()


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

try:

    feature_names = joblib.load(
        "feature_names_v2.pkl"
    )

    model_rf = model.named_steps["rf"]

    importance = pd.DataFrame({

        "Feature": feature_names,

        "Importance": model_rf.feature_importances_

    })

    importance = importance.sort_values(

        "Importance",

        ascending=False

    )

    importance.to_csv(

        "feature_importance.csv",

        index=False

    )

except Exception as e:

    print(

        "Feature importance skipped:",

        e

    )


    # ============================================================
# SAVE METRICS
# ============================================================

metrics = {

    "accuracy": float(accuracy),

    "precision": float(precision),

    "recall": float(recall),

    "f1_score": float(f1),

    "roc_auc": float(roc)

}

with open(

    "training_metrics.json",

    "w"

) as f:

    json.dump(

        metrics,

        f,

        indent=4

    )


    # ============================================================
# DONE
# ============================================================

print("\nEvaluation Complete")

print("----------------------------")

print("training_metrics.json")

print("feature_importance.csv")

print("confusion_matrix.png")

print("roc_curve.png")

print("precision_recall_curve.png")