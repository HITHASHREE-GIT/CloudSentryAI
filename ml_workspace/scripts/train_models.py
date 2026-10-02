"""
CloudSentry AI — Model Training & Comparison
=============================================
Trains 3 tabular ML models on the synthetic dataset:
  1. Gradient Boosting  (baseline — already in project docs)
  2. Random Forest      (bagging ensemble)
  3. XGBoost            (optimized gradient boosting)

Compares precision, recall, F1, ROC-AUC on the same train/test split.

Selects best model by WEIGHTED F1 SCORE — with evidence, not hype.

Saves:
  - models/gradient_boosting.pkl
  - models/random_forest.pkl
  - models/xgboost.pkl
  - models/best_model.pkl
  - models/comparison_report.json
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from xgboost import XGBClassifier
import joblib

# ─── Paths ───
ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "datasets" / "synthetic_configs.csv"
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42


def load_data():
    df = pd.read_csv(DATASET)
    X = df.drop("priority", axis=1)
    y = df["priority"]

    # Convert bools to ints (sklearn friendly)
    X = X.astype(int)

    print(f"📂 Loaded dataset: {X.shape[0]} rows, {X.shape[1]} features")
    print(f"   Classes: {sorted(y.unique())}")
    return X, y


def train_and_evaluate(name: str, model, X_train, X_test, y_train, y_test):
    """Train one model and return metrics."""
    print(f"\n🔧 Training {name}...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # ROC-AUC needs probabilities (one-vs-rest for multiclass)
    try:
        y_proba = model.predict_proba(X_test)
        roc_auc = roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted")
    except Exception:
        roc_auc = None

    metrics = {
        "model": name,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        "roc_auc": float(roc_auc) if roc_auc is not None else None,
    }

    print(f"   ✅ Accuracy : {metrics['accuracy']:.4f}")
    print(f"   ✅ Precision: {metrics['precision']:.4f}")
    print(f"   ✅ Recall   : {metrics['recall']:.4f}")
    print(f"   ✅ F1       : {metrics['f1']:.4f}")
    if roc_auc is not None:
        print(f"   ✅ ROC-AUC  : {metrics['roc_auc']:.4f}")

    return model, metrics


def main():
    # ─── Load ───
    X, y = load_data()

    # ─── Split ───
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")

        # ─── Feature scaling ───
    # Use .values (numpy arrays without feature names) so the scaler
    # can transform raw arrays at inference time without warnings.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train.values)
    X_test_scaled = scaler.transform(X_test.values)

    # ─── Define models ───
    models = [
        (
            "Gradient Boosting",
            GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=RANDOM_STATE,
            ),
        ),
        (
            "Random Forest",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
        ),
        (
            "XGBoost",
            XGBClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                random_state=RANDOM_STATE,
                eval_metric="mlogloss",
                use_label_encoder=False,
            ),
        ),
    ]

    # ─── Train all ───
    results = []
    trained_models = {}

    for name, model in models:
        trained, metrics = train_and_evaluate(
            name, model, X_train_scaled, X_test_scaled, y_train, y_test
        )
        results.append(metrics)
        trained_models[name] = trained

        # Save individual model
        filename = name.lower().replace(" ", "_") + ".pkl"
        joblib.dump(trained, MODELS_DIR / filename)
        print(f"   💾 Saved: {filename}")

    # ─── Compare ───
    print()
    print("=" * 72)
    print("📊 MODEL COMPARISON")
    print("=" * 72)
    print(f"{'Model':<20} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'ROC-AUC':>10}")
    print("-" * 72)
    for r in results:
        roc = f"{r['roc_auc']:.4f}" if r["roc_auc"] is not None else "—"
        print(
            f"{r['model']:<20} {r['accuracy']:>10.4f} {r['precision']:>10.4f} "
            f"{r['recall']:>10.4f} {r['f1']:>10.4f} {roc:>10}"
        )
    print("=" * 72)

    # ─── Select best by F1 ───
    best = max(results, key=lambda r: r["f1"])
    print(f"\n🏆 Best model: {best['model']} (F1 = {best['f1']:.4f})")

    # Save best model
    joblib.dump(trained_models[best["model"]], MODELS_DIR / "best_model.pkl")
    print(f"💾 Saved best model: models/best_model.pkl")

    # Save scaler
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    print(f"💾 Saved scaler: models/scaler.pkl")

    # Save report
    report = {
        "dataset": str(DATASET.name),
        "n_samples": int(len(X)),
        "n_features": int(X.shape[1]),
        "test_size": 0.20,
        "random_state": RANDOM_STATE,
        "results": results,
        "best_model": best["model"],
        "selection_metric": "weighted F1",
        "best_f1": best["f1"],
    }
    with open(MODELS_DIR / "comparison_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"💾 Saved report: models/comparison_report.json")

    print()
    print("=" * 72)
    print("✅ Training complete")
    print("=" * 72)


if __name__ == "__main__":
    main()