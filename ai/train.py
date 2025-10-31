#!/usr/bin/env python3
"""
Training script for the anomaly detection model.
Loads log data and trains the model for deployment.
"""

import sys
from pathlib import Path

# Add parent directory to path before importing model
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np  # noqa: E402
import json  # noqa: E402
import argparse  # noqa: E402

from model.anomaly_detector import AnomalyDetector  # noqa: E402


def load_training_data(data_path):
    """Load training data from file."""
    if data_path.endswith('.json'):
        with open(data_path, 'r') as f:
            data = json.load(f)
            return np.array(data['features'])
    elif data_path.endswith('.npy'):
        return np.load(data_path)
    else:
        raise ValueError("Unsupported file format. Use .json or .npy")


def generate_synthetic_data(n_samples=1000, n_features=20):
    """Generate synthetic training data for testing."""
    return np.random.randn(n_samples, n_features)


def main():
    parser = argparse.ArgumentParser(description='Train anomaly detection model')
    parser.add_argument(
        '--data',
        type=str,
        help='Path to training data file (.json or .npy)'
    )
    parser.add_argument(
        '--synthetic',
        action='store_true',
        help='Use synthetic data for training'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=50,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for training'
    )
    parser.add_argument(
        '--input-dim',
        type=int,
        default=20,
        help='Input feature dimension'
    )
    parser.add_argument(
        '--encoding-dim',
        type=int,
        default=10,
        help='Encoding dimension'
    )
    parser.add_argument(
        '--model-name',
        type=str,
        default='anomaly_detector',
        help='Name for saving the model'
    )

    args = parser.parse_args()

    # Initialize detector
    print(f"Initializing Anomaly Detector (input_dim={args.input_dim}, encoding_dim={args.encoding_dim})...")
    detector = AnomalyDetector(input_dim=args.input_dim, encoding_dim=args.encoding_dim)

    # Load or generate training data
    if args.synthetic:
        print("Generating synthetic training data...")
        X_train = generate_synthetic_data(n_samples=1000, n_features=args.input_dim)
    elif args.data:
        print(f"Loading training data from {args.data}...")
        X_train = load_training_data(args.data)
    else:
        print("No data source specified. Using synthetic data...")
        X_train = generate_synthetic_data(n_samples=1000, n_features=args.input_dim)

    print(f"Training data shape: {X_train.shape}")

    # Train model
    print(f"Training model for {args.epochs} epochs...")
    history = detector.train(
        X_train,
        epochs=args.epochs,
        batch_size=args.batch_size
    )

    print("\nTraining complete!")
    print(f"Final loss: {history.history['loss'][-1]:.4f}")
    print(f"Anomaly threshold: {detector.threshold:.4f}")

    # Save model
    print(f"\nSaving model as '{args.model_name}'...")
    detector.save_model(name=args.model_name)

    print("\nModel training and saving completed successfully!")


if __name__ == "__main__":
    main()
