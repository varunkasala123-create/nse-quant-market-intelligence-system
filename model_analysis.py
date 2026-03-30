import joblib
import pandas as pd


def feature_importance(model_path, features):

    model = joblib.load(model_path)

    importance = model.feature_importances_

    df = pd.DataFrame({
        "feature":features,
        "importance":importance
    })

    df = df.sort_values("importance",ascending=False)

    print("\n===== FEATURE IMPORTANCE =====\n")

    print(df.head(20))