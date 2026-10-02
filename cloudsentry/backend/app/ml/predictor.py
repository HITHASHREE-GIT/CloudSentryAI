"""
CloudSentry AI — ML Predictor
==============================
Loads the trained model and predicts priority for findings.

The model was trained on synthetic cloud configuration data
and predicts a priority class:
  0 = Low
  1 = Medium
  2 = High
  3 = Critical

Used as an ADDITIONAL signal alongside rule-based severity.
"""

from pathlib import Path
import joblib
import numpy as np

from app.models import Finding

# ─── Paths ───
ML_DIR = Path(__file__).resolve().parent
MODEL_PATH = ML_DIR / "best_model.pkl"
SCALER_PATH = ML_DIR / "scaler.pkl"

PRIORITY_LABELS = {
    0: "LOW",
    1: "MEDIUM",
    2: "HIGH",
    3: "CRITICAL",
}


class MLPredictor:
    """Wraps the trained model for finding-priority prediction."""

    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)

    # ─────────────────────────────────────────────
    # FEATURE EXTRACTION
    # ─────────────────────────────────────────────

    def _finding_to_features(self, finding: Finding) -> np.ndarray:
        """
        Convert a Finding into the 9-feature vector the model expects:
          public_access, encryption_enabled, logging_enabled,
          mfa_enabled, internet_exposed, iam_privilege,
          resource_criticality, resource_age_days, change_frequency

        Feature extraction is RULE-SPECIFIC — each rule sets the fields
        that best describe the misconfiguration it detected.
        """
        evidence = finding.evidence or {}
        rule_id = finding.rule_id

        # ─── Defaults (neutral) ───
        public_access = 0
        encryption_enabled = 1
        logging_enabled = 1
        mfa_enabled = 1
        iam_privilege = 0
        resource_age_days = 365
        change_frequency = 10

        # ─── RULE-SPECIFIC MAPPING ───

        if rule_id == "PUBLIC_S3_RULE":
            public_access = 1
            encryption_enabled = 0
            logging_enabled = 0

        elif rule_id == "SSH_EXPOSED_RULE":
            public_access = 1
            if evidence.get("source") != "0.0.0.0/0":
                public_access = 0

        elif rule_id == "EXCESSIVE_IAM_RULE":
            policies = evidence.get("excessive_policies", [])
            if "AdministratorAccess" in policies:
                iam_privilege = 3
            elif "PowerUserAccess" in policies:
                iam_privilege = 2

        elif rule_id == "STALE_KEY_RULE":
            keys = evidence.get("stale_keys", [])
            if keys:
                resource_age_days = keys[0].get("created_days_ago", 365)

        elif rule_id == "UNUSED_USER_RULE":
            resource_age_days = evidence.get("last_activity_days_ago", 365)

        elif rule_id == "CLOUDTRAIL_DISABLED_RULE":
            logging_enabled = 0

        elif rule_id == "UNENCRYPTED_STORAGE_RULE":
            encryption_enabled = 0

        elif rule_id == "ROOT_MFA_RULE":
            mfa_enabled = 0

        internet_exposed = public_access

        # ─── Resource criticality from severity ───
        criticality_map = {
            "CRITICAL": 5,
            "HIGH": 4,
            "MEDIUM": 3,
            "LOW": 2,
        }
        resource_criticality = criticality_map.get(finding.severity.upper(), 3)

        # ─── Build feature vector ───
        features = np.array([[
            public_access,
            encryption_enabled,
            logging_enabled,
            mfa_enabled,
            internet_exposed,
            iam_privilege,
            resource_criticality,
            resource_age_days,
            change_frequency,
        ]])

        return features

    # ─────────────────────────────────────────────
    # PREDICT
    # ─────────────────────────────────────────────

    def predict(self, finding: Finding) -> dict:
        """Return ML-predicted priority + confidence."""
        import warnings
        X = self._finding_to_features(finding)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            X_scaled = self.scaler.transform(X)
            pred = int(self.model.predict(X_scaled)[0])
            proba = self.model.predict_proba(X_scaled)[0]

        confidence = float(max(proba))

        return {
            "ml_priority": PRIORITY_LABELS[pred],
            "ml_priority_score": pred,
            "ml_confidence": round(confidence, 4),
        }
        return {
            "ml_priority": PRIORITY_LABELS[pred],
            "ml_priority_score": pred,
            "ml_confidence": round(confidence, 4),
        }


# ─── Singleton instance ───
_predictor: MLPredictor | None = None


def get_predictor() -> MLPredictor:
    global _predictor
    if _predictor is None:
        _predictor = MLPredictor()
    return _predictor