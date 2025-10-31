"""
Tests for anomaly detection model
"""

import pytest
import numpy as np
from model.anomaly_detector import AnomalyDetector, generate_recommendations


class TestAnomalyDetector:
    """Test cases for AnomalyDetector class"""

    def test_model_initialization(self):
        """Test that model initializes with correct parameters"""
        detector = AnomalyDetector(input_dim=20, encoding_dim=10)
        assert detector.input_dim == 20
        assert detector.encoding_dim == 10
        assert detector.model is None
        assert detector.threshold is None

    def test_build_model(self):
        """Test model building"""
        detector = AnomalyDetector(input_dim=20, encoding_dim=10)
        model = detector.build_model()
        assert model is not None
        assert detector.model is not None

    def test_train_model(self):
        """Test model training with synthetic data"""
        detector = AnomalyDetector(input_dim=20, encoding_dim=10)
        X_train = np.random.randn(100, 20)

        history = detector.train(X_train, epochs=5, batch_size=16)

        assert detector.model is not None
        assert detector.threshold is not None
        assert detector.threshold > 0
        assert "loss" in history.history

    def test_predict_anomalies(self):
        """Test anomaly prediction"""
        detector = AnomalyDetector(input_dim=20, encoding_dim=10)
        X_train = np.random.randn(100, 20)
        detector.train(X_train, epochs=5, batch_size=16)

        # Test with normal data
        X_test = np.random.randn(50, 20)
        results = detector.predict(X_test)

        assert "anomaly_scores" in results
        assert "is_anomaly" in results
        assert "threshold" in results
        assert "anomaly_count" in results
        assert len(results["anomaly_scores"]) == 50
        assert len(results["is_anomaly"]) == 50

    def test_predict_with_anomalies(self):
        """Test that anomalies are correctly detected"""
        detector = AnomalyDetector(input_dim=20, encoding_dim=10)
        X_train = np.random.randn(100, 20)
        detector.train(X_train, epochs=5, batch_size=16)

        # Create obvious anomalies
        X_test = np.random.randn(10, 20) * 5  # Scaled up significantly
        results = detector.predict(X_test)

        # Should detect some anomalies
        assert results["anomaly_count"] > 0

    def test_predict_without_training(self):
        """Test that prediction fails without training"""
        detector = AnomalyDetector(input_dim=20, encoding_dim=10)
        X_test = np.random.randn(10, 20)

        with pytest.raises(ValueError):
            detector.predict(X_test)


class TestRecommendations:
    """Test cases for recommendation generation"""

    def test_low_severity(self):
        """Test low severity recommendations"""
        anomaly_results = {"anomaly_count": 5, "is_anomaly": [False] * 95 + [True] * 5}
        current_state = {"node_count": 3}

        recommendations = generate_recommendations(anomaly_results, current_state)

        assert recommendations["severity"] == "low"
        assert len(recommendations["actions"]) == 0

    def test_medium_severity(self):
        """Test medium severity recommendations"""
        anomaly_results = {"anomaly_count": 15, "is_anomaly": [False] * 85 + [True] * 15}
        current_state = {"node_count": 3}

        recommendations = generate_recommendations(anomaly_results, current_state)

        assert recommendations["severity"] == "medium"
        assert len(recommendations["actions"]) > 0

    def test_high_severity(self):
        """Test high severity recommendations"""
        anomaly_results = {"anomaly_count": 30, "is_anomaly": [False] * 70 + [True] * 30}
        current_state = {"node_count": 3}

        recommendations = generate_recommendations(anomaly_results, current_state)

        assert recommendations["severity"] == "high"
        assert any(action["type"] == "scale_up" for action in recommendations["actions"])

    def test_critical_severity(self):
        """Test critical severity recommendations"""
        anomaly_results = {"anomaly_count": 60, "is_anomaly": [False] * 40 + [True] * 60}
        current_state = {"node_count": 3}

        recommendations = generate_recommendations(anomaly_results, current_state)

        assert recommendations["severity"] == "critical"
        assert any(action["type"] == "scale_up" for action in recommendations["actions"])
        assert any(action["type"] == "rotate_honeypots" for action in recommendations["actions"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
