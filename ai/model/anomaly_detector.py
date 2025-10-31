import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
import pickle
from datetime import datetime
from pathlib import Path

class AnomalyDetector:
    """
    ML model for detecting anomalous behavior in honeypot logs.
    Uses an autoencoder architecture for unsupervised anomaly detection.
    """

    def __init__(self, input_dim=20, encoding_dim=10):
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim
        self.model = None
        self.scaler = StandardScaler()
        self.threshold = None
        self.model_dir = Path(__file__).parent / "saved_models"
        self.model_dir.mkdir(exist_ok=True)

    def build_model(self):
        """Build autoencoder model for anomaly detection."""
        # Encoder
        input_layer = keras.Input(shape=(self.input_dim,))
        encoded = keras.layers.Dense(
            self.encoding_dim * 2,
            activation='relu'
        )(input_layer)
        encoded = keras.layers.Dropout(0.2)(encoded)
        encoded = keras.layers.Dense(
            self.encoding_dim,
            activation='relu'
        )(encoded)

        # Decoder
        decoded = keras.layers.Dense(
            self.encoding_dim * 2,
            activation='relu'
        )(encoded)
        decoded = keras.layers.Dropout(0.2)(decoded)
        decoded = keras.layers.Dense(
            self.input_dim,
            activation='sigmoid'
        )(decoded)

        # Autoencoder model
        self.model = keras.Model(input_layer, decoded)
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )

        return self.model

    def train(self, X_train, epochs=50, batch_size=32, validation_split=0.2):
        """
        Train the anomaly detection model.

        Args:
            X_train: Training data (normal behavior)
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of data to use for validation
        """
        if self.model is None:
            self.build_model()

        # Normalize data
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Train model
        history = self.model.fit(
            X_train_scaled,
            X_train_scaled,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            shuffle=True,
            verbose=1
        )

        # Calculate reconstruction error threshold
        reconstructions = self.model.predict(X_train_scaled)
        mse = np.mean(np.power(X_train_scaled - reconstructions, 2), axis=1)
        self.threshold = np.percentile(mse, 95)  # 95th percentile

        return history

    def predict(self, X):
        """
        Predict anomalies in new data.

        Args:
            X: Input data to check for anomalies

        Returns:
            Dictionary with predictions, scores, and anomaly flags
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")

        X_scaled = self.scaler.transform(X)
        reconstructions = self.model.predict(X_scaled)
        mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)

        anomalies = mse > self.threshold

        return {
            'anomaly_scores': mse.tolist(),
            'is_anomaly': anomalies.tolist(),
            'threshold': float(self.threshold),
            'anomaly_count': int(np.sum(anomalies))
        }

    def save_model(self, name='anomaly_detector'):
        """Save the trained model and scaler."""
        model_path = self.model_dir / f"{name}.h5"
        scaler_path = self.model_dir / f"{name}_scaler.pkl"
        config_path = self.model_dir / f"{name}_config.json"

        self.model.save(model_path)

        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

        config = {
            'threshold': float(self.threshold),
            'input_dim': self.input_dim,
            'encoding_dim': self.encoding_dim,
            'saved_at': datetime.now().isoformat()
        }

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"Model saved to {model_path}")

    def load_model(self, name='anomaly_detector'):
        """Load a previously trained model and scaler."""
        model_path = self.model_dir / f"{name}.h5"
        scaler_path = self.model_dir / f"{name}_scaler.pkl"
        config_path = self.model_dir / f"{name}_config.json"

        self.model = keras.models.load_model(model_path)

        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)

        with open(config_path, 'r') as f:
            config = json.load(f)
            self.threshold = config['threshold']

        print(f"Model loaded from {model_path}")


def generate_recommendations(anomaly_results, current_state):
    """
    Generate infrastructure recommendations based on anomaly detection results.

    Args:
        anomaly_results: Results from anomaly detection
        current_state: Current infrastructure state

    Returns:
        Dictionary with recommendations
    """
    recommendations = {
        'timestamp': datetime.now().isoformat(),
        'anomaly_count': anomaly_results['anomaly_count'],
        'severity': 'low',
        'actions': []
    }

    anomaly_rate = anomaly_results['anomaly_count'] / len(anomaly_results['is_anomaly'])

    if anomaly_rate > 0.5:
        recommendations['severity'] = 'critical'
        recommendations['actions'].append({
            'type': 'scale_up',
            'reason': 'High anomaly rate detected',
            'parameter': 'node_count',
            'suggested_value': current_state.get('node_count', 3) + 2
        })
        recommendations['actions'].append({
            'type': 'rotate_honeypots',
            'reason': 'Possible detection by attackers',
            'parameter': 'honeypot_config',
            'suggested_value': 'rotate_all'
        })
    elif anomaly_rate > 0.2:
        recommendations['severity'] = 'high'
        recommendations['actions'].append({
            'type': 'scale_up',
            'reason': 'Elevated anomaly rate',
            'parameter': 'node_count',
            'suggested_value': current_state.get('node_count', 3) + 1
        })
    elif anomaly_rate > 0.1:
        recommendations['severity'] = 'medium'
        recommendations['actions'].append({
            'type': 'monitor',
            'reason': 'Moderate anomaly activity',
            'parameter': 'alert_threshold',
            'suggested_value': 'increase_sensitivity'
        })

    return recommendations


if __name__ == "__main__":
    # Example usage
    print("Initializing Anomaly Detector...")
    detector = AnomalyDetector(input_dim=20, encoding_dim=10)

    # Generate synthetic training data (replace with actual log data)
    print("Generating synthetic training data...")
    X_train = np.random.randn(1000, 20)

    # Train model
    print("Training model...")
    detector.train(X_train, epochs=30, batch_size=32)

    # Save model
    detector.save_model()

    # Generate test data with some anomalies
    X_test = np.random.randn(100, 20)
    X_test[-10:] += 3  # Add anomalies

    # Make predictions
    print("\nMaking predictions...")
    results = detector.predict(X_test)
    print(f"Detected {results['anomaly_count']} anomalies out of {len(X_test)} samples")

    # Generate recommendations
    current_state = {'node_count': 3}
    recommendations = generate_recommendations(results, current_state)
    print(f"\nRecommendations: {json.dumps(recommendations, indent=2)}")
