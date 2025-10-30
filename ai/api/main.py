from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from model.anomaly_detector import AnomalyDetector, generate_recommendations

app = FastAPI(
    title="Project Asylum AI API",
    description="AI/ML API for anomaly detection and infrastructure recommendations",
    version="1.0.0"
)

# Global model instance
detector = AnomalyDetector(input_dim=20, encoding_dim=10)
state_file = Path(__file__).parent.parent / "data" / "state.json"
state_file.parent.mkdir(exist_ok=True)


class LogData(BaseModel):
    """Model for log data input"""
    features: List[List[float]] = Field(..., description="Feature matrix for analysis")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class TrainingData(BaseModel):
    """Model for training data"""
    features: List[List[float]] = Field(..., description="Training feature matrix")
    epochs: int = Field(default=50, description="Number of training epochs")
    batch_size: int = Field(default=32, description="Batch size for training")


class PredictionResponse(BaseModel):
    """Model for prediction response"""
    anomaly_scores: List[float]
    is_anomaly: List[bool]
    threshold: float
    anomaly_count: int
    timestamp: str


class RecommendationResponse(BaseModel):
    """Model for recommendation response"""
    timestamp: str
    anomaly_count: int
    severity: str
    actions: List[Dict[str, Any]]
    state_updated: bool


def load_current_state() -> Dict[str, Any]:
    """Load current infrastructure state"""
    if state_file.exists():
        with open(state_file, 'r') as f:
            return json.load(f)
    return {
        'node_count': 3,
        'last_update': datetime.now().isoformat(),
        'recommendations': []
    }


def save_state(state: Dict[str, Any]):
    """Save infrastructure state"""
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Project Asylum AI API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": detector.model is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/train", response_model=Dict[str, Any])
async def train_model(data: TrainingData, background_tasks: BackgroundTasks):
    """
    Train the anomaly detection model with provided data.
    """
    try:
        X_train = np.array(data.features)
        
        if X_train.shape[1] != detector.input_dim:
            raise HTTPException(
                status_code=400,
                detail=f"Feature dimension mismatch. Expected {detector.input_dim}, got {X_train.shape[1]}"
            )
        
        # Train model
        history = detector.train(
            X_train,
            epochs=data.epochs,
            batch_size=data.batch_size
        )
        
        # Save model in background
        background_tasks.add_task(detector.save_model)
        
        return {
            "status": "success",
            "message": "Model trained successfully",
            "epochs": data.epochs,
            "final_loss": float(history.history['loss'][-1]),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictionResponse)
async def predict_anomalies(data: LogData):
    """
    Predict anomalies in provided log data.
    """
    try:
        if detector.model is None:
            # Try to load existing model
            try:
                detector.load_model()
            except:
                raise HTTPException(
                    status_code=400,
                    detail="Model not trained. Please train the model first."
                )
        
        X = np.array(data.features)
        
        if X.shape[1] != detector.input_dim:
            raise HTTPException(
                status_code=400,
                detail=f"Feature dimension mismatch. Expected {detector.input_dim}, got {X.shape[1]}"
            )
        
        results = detector.predict(X)
        results['timestamp'] = datetime.now().isoformat()
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=RecommendationResponse)
async def analyze_and_recommend(data: LogData):
    """
    Analyze log data and generate infrastructure recommendations.
    """
    try:
        if detector.model is None:
            try:
                detector.load_model()
            except:
                raise HTTPException(
                    status_code=400,
                    detail="Model not trained. Please train the model first."
                )
        
        X = np.array(data.features)
        
        # Get predictions
        anomaly_results = detector.predict(X)
        
        # Load current state
        current_state = load_current_state()
        
        # Generate recommendations
        recommendations = generate_recommendations(anomaly_results, current_state)
        
        # Update state
        current_state['last_analysis'] = datetime.now().isoformat()
        current_state['last_anomaly_count'] = anomaly_results['anomaly_count']
        current_state['recommendations'] = recommendations['actions']
        
        # Save state
        save_state(current_state)
        
        recommendations['state_updated'] = True
        
        return recommendations
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state")
async def get_state():
    """
    Get current infrastructure state and recommendations.
    """
    try:
        state = load_current_state()
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info")
async def model_info():
    """
    Get information about the current model.
    """
    return {
        "model_loaded": detector.model is not None,
        "input_dim": detector.input_dim,
        "encoding_dim": detector.encoding_dim,
        "threshold": detector.threshold if detector.threshold else None,
        "model_dir": str(detector.model_dir)
    }


@app.post("/model/load")
async def load_model(name: str = "anomaly_detector"):
    """
    Load a previously saved model.
    """
    try:
        detector.load_model(name)
        return {
            "status": "success",
            "message": f"Model '{name}' loaded successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to load model: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
