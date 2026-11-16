"""
JOLODHAR - ML Prediction Service
Loads trained RandomForest model and provides real-time predictions
"""

import os
import sys
import json
import logging
import numpy as np
import joblib

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

logger = logging.getLogger(__name__)


class DrainPredictor:
    """Load trained model and predict drain status"""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.metrics = None
        self.feature_columns = None
        self._load()

    def _load(self):
        """Load model, scaler, metrics, feature columns"""
        try:
            model_path = os.path.join(BASE_DIR, "ml", "model.pkl")
            scaler_path = os.path.join(BASE_DIR, "ml", "scaler.pkl")
            metrics_path = os.path.join(BASE_DIR, "ml", "metrics.json")
            feature_cols_path = os.path.join(BASE_DIR, "ml", "feature_columns.json")

            if not os.path.exists(model_path):
                logger.warning("Model file not found. Run: python ml/train_model.py")
                return

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)

            if os.path.exists(metrics_path):
                with open(metrics_path, "r", encoding="utf-8") as f:
                    self.metrics = json.load(f)

            if os.path.exists(feature_cols_path):
                with open(feature_cols_path, "r", encoding="utf-8") as f:
                    self.feature_columns = json.load(f)

            logger.info("ML model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None

    @property
    def is_loaded(self):
        return self.model is not None

    def predict(self, features_dict):
        """
        Predict drain status from features
        Args:
            features_dict: dict with keys matching FEATURE_COLUMNS
        Returns:
            dict with prediction, probabilities, risk levels
        """
        if not self.is_loaded:
            return {"error": "Model not loaded"}

        # Build feature vector in correct order
        feature_vector = []
        for col in self.feature_columns:
            feature_vector.append(float(features_dict.get(col, 0)))

        X = np.array([feature_vector])
        X_scaled = self.scaler.transform(X)

        prediction = int(self.model.predict(X_scaled)[0])
        probabilities = self.model.predict_proba(X_scaled)[0]

        class_names = self.metrics.get("class_names", ["Normal", "Warning", "Critical"])
        class_names_bn = self.metrics.get("class_names_bn", ["স্বাভাবিক", "সতর্কতা", "সংকটাপন্ন"])

        # Risk scores
        risk_levels = {
            "blockage_risk": float(probabilities[1] * 0.5 + probabilities[2] * 1.0),  # weighted
            "flood_risk": float(probabilities[2]),
            "normal_score": float(probabilities[0]),
        }

        return {
            "prediction": prediction,
            "predicted_class": class_names[prediction],
            "predicted_class_bn": class_names_bn[prediction],
            "probabilities": {
                class_names[i]: float(probabilities[i]) for i in range(len(class_names))
            },
            "probabilities_bn": {
                class_names_bn[i]: float(probabilities[i]) for i in range(len(class_names_bn))
            },
            "risk_levels": risk_levels,
            "input_features": features_dict,
            "model_accuracy": self.metrics.get("accuracy", 0) if self.metrics else 0,
        }

    def get_metrics(self):
        """Return model metrics dict"""
        return self.metrics or {}

    def get_feature_importance(self):
        """Return feature importance list"""
        if self.metrics and "feature_importance" in self.metrics:
            return self.metrics["feature_importance"]
        return []


# Singleton
drain_predictor = DrainPredictor()
