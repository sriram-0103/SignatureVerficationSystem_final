import json
import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline

from sklearn.preprocessing import StandardScaler

from sklearn.model_selection import (

    train_test_split,

    RandomizedSearchCV,

    StratifiedKFold

)

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (

    accuracy_score,

    classification_report,

    confusion_matrix

)

from feature_extractor import FEATURE_ORDER

# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading Dataset...")

df = pd.read_csv("training_dataset.csv")

missing = [

    f

    for f in FEATURE_ORDER

    if f not in df.columns

]

if missing:

    raise ValueError(

        f"Missing Features : {missing}"

    )

X = df[FEATURE_ORDER]

y = df["label"]

print(df.shape)

# ============================================================
# TRAIN TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.20,

    random_state=42,

    stratify=y

)

print(

    "\nTraining Samples :",

    len(X_train)

)

print(

    "Testing Samples :",

    len(X_test)

)

# ============================================================
# PIPELINE
# ============================================================

pipeline = Pipeline(

    [

        (

            "scaler",

            StandardScaler()

        ),

        (

            "rf",

            RandomForestClassifier(

                random_state=42,

                n_jobs=-1

            )

        )

    ]

)


# ============================================================
# RANDOM SEARCH
# ============================================================

param_grid = {

    "rf__n_estimators":[
        200,
        300,
        400,
        500
    ],

    "rf__max_depth":[
        10,
        20,
        30,
        None
    ],

    "rf__min_samples_split":[
        2,
        4,
        6,
        8
    ],

    "rf__min_samples_leaf":[
        1,
        2,
        3,
        4
    ],

    "rf__max_features":[
        "sqrt",
        "log2"
    ],

    "rf__bootstrap":[
        True,
        False
    ]

}

search = RandomizedSearchCV(

    estimator=pipeline,

    param_distributions=param_grid,

    n_iter=20,

    cv=StratifiedKFold(

        n_splits=5,

        shuffle=True,

        random_state=42

    ),

    scoring="accuracy",

    random_state=42,

    n_jobs=-1,

    verbose=2,

    refit=True

)

print("\nSearching Best Parameters...\n")

search.fit(

    X_train,

    y_train

)

best_model = search.best_estimator_

print("\nBest Parameters")

print(search.best_params_)


# ============================================================
# TESTING
# ============================================================

prediction = best_model.predict(

    X_test

)

accuracy = accuracy_score(

    y_test,

    prediction

)

print("\nAccuracy")

print(round(

    accuracy * 100,

    2

), "%")

print(

    classification_report(

        y_test,

        prediction

    )

)

cm = confusion_matrix(

    y_test,

    prediction

)

print("\nConfusion Matrix")

print(cm)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(

    best_model,

    "signature_forgery_model_v2.pkl"

)

joblib.dump(

    FEATURE_ORDER,

    "feature_names_v2.pkl"

)

np.save(

    "X_test.npy",

    X_test.values

)

np.save(

    "y_test.npy",

    y_test.values

)

metadata = {

    "model":"Random Forest",

    "version":"2.0",

    "dataset":"SVC2004 Task1 + Task2",

    "features":len(FEATURE_ORDER),

    "training_samples":int(

        len(X_train)

    ),

    "testing_samples":int(

        len(X_test)

    ),

    "accuracy":float(

        accuracy

    ),

    "best_parameters":search.best_params_,

    "random_state":42

}

with open(

    "metadata.json",

    "w"

) as f:

    json.dump(

        metadata,

        f,

        indent=4

    )

print("\nSaved Files")

print("---------------------------")

print("signature_forgery_model_v2.pkl")

print("feature_names_v2.pkl")

print("X_test.npy")

print("y_test.npy")

print("metadata.json")


