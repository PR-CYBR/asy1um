"""
Basic tests for FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import app

client = TestClient(app)


class TestAPI:
    """Test cases for API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "Project Asylum AI API"

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_model_info_endpoint(self):
        """Test model info endpoint"""
        response = client.get("/model/info")
        assert response.status_code == 200
        data = response.json()
        assert "model_loaded" in data
        assert "input_dim" in data

    def test_state_endpoint(self):
        """Test state endpoint"""
        response = client.get("/state")
        assert response.status_code == 200
        # Should return current state
        assert response.json() is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
