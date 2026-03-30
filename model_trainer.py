import pandas as pd
import numpy as np
import joblib

from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score

from feature_engine import add_features


def train_model(df, horizon=5, model_name="models/trading_model.pkl"):

    # ===============================
    # Combine dataset list
    # ===============================

    if isinstance(df, list):
        df = pd.concat(df)

    # ===============================
    # Sort dataset (critical)
    # ===============================

    if "timestamp" in df.columns:
        df = df.sort_values("timestamp")

    print("\nTotal dataset rows:", len(df))

    # ===============================
    # Feature Engineering
    # ===============================

    df = add_features(df)

    # ===============================
    # ATR Normalized Label
    # ===============================

    future_price = df["close"].shift(-horizon)

    future_return = (future_price - df["close"]) / df["close"]

    # Use ATR already calculated in feature_engine
    atr = df["atr"]

    atr_pct = atr / df["close"]

    threshold = atr_pct * 0.25

    df["target"] = np.where(
        future_return > threshold, 1,
        np.where(future_return < -threshold, 0, np.nan)
    )

    # ===============================
    # Clean data
    # ===============================

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    # ===============================
    # Feature selection
    # ===============================

    feature_cols = df.columns.tolist()

    for col in ["target", "symbol", "timestamp"]:
        if col in feature_cols:
            feature_cols.remove(col)

    X = df[feature_cols]
    y = df["target"]

    # ===============================
    # Walk forward split
    # ===============================

    split = int(len(df) * 0.8)

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    # GPU stability
    X_train = X_train.astype(np.float32)
    X_test = X_test.astype(np.float32)

    print("Training rows:", len(X_train))
    print("Validation rows:", len(X_test))
    print("Features used:", len(feature_cols))

    # ===============================
    # LightGBM Model
    # ===============================

    model = LGBMClassifier(

        n_estimators=700,
        learning_rate=0.03,

        max_depth=6,
        num_leaves=64,

        min_child_samples=20,

        subsample=0.8,
        colsample_bytree=0.8,

        reg_alpha=0.1,
        reg_lambda=0.1,

        class_weight="balanced",

        random_state=42,

        device="gpu",
        gpu_platform_id=0,
        gpu_device_id=0

    )

    # ===============================
    # Train model
    # ===============================

    model.fit(X_train, y_train)

    # ===============================
    # Validation
    # ===============================

    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)

    prob = model.predict_proba(X_test)[:,1]

    print("\nModel accuracy:", acc)

    print("Mean prediction confidence:", round(prob.mean(),3))

    print("Prediction std:", round(prob.std(),3))

    # ===============================
    # Save model
    # ===============================

    joblib.dump(model, model_name)

    print("Model saved:", model_name)

    return model