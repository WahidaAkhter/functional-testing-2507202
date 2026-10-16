"""Tests for the web application endpoints, health checks, and runner API."""

from fastapi.testclient import TestClient
import pytest

from app import app, get_current_commit_sha


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Test that /health returns status ok and a commit SHA."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "commit_sha" in data
    assert isinstance(data["commit_sha"], str)
    assert len(data["commit_sha"]) > 0


def test_get_current_commit_sha_env(monkeypatch):
    """Test commit SHA resolution from environment variables."""
    monkeypatch.setenv("COMMIT_SHA", "abcdef1234567890")
    assert get_current_commit_sha() == "abcdef1234567890"


def test_api_functions_catalog(client):
    """Test that /api/functions returns the 16 target functions."""
    response = client.get("/api/functions")
    assert response.status_code == 200
    data = response.json()
    assert "functions" in data
    assert len(data["functions"]) == 16
    names = [fn["name"] for fn in data["functions"]]
    assert "is_adult" in names
    assert "average" in names


def test_api_run_valid_function(client):
    """Test executing a valid function returns 200 and expected result."""
    payload = {
        "function_name": "is_adult",
        "arguments": {"age": 20},
    }
    response = client.post("/api/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["result"] is True
    assert data["result_type"] == "bool"


def test_api_run_celsius_to_fahrenheit(client):
    """Test celsius_to_fahrenheit execution."""
    payload = {
        "function_name": "celsius_to_fahrenheit",
        "arguments": {"celsius": 100},
    }
    response = client.post("/api/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["result"] == 212.0


def test_api_run_error_handling(client):
    """Test executing a function that raises an exception returns 400 and error detail."""
    payload = {
        "function_name": "divide",
        "arguments": {"a": 10, "b": 0},
    }
    response = client.post("/api/run", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "ZeroDivisionError"
    assert "cannot divide by zero" in data["error_message"]


def test_api_run_unknown_function(client):
    """Test executing an unknown function returns 404."""
    payload = {
        "function_name": "non_existent_function",
        "arguments": {},
    }
    response = client.post("/api/run", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "NotFoundError"


def test_index_page(client):
    """Test serving the index HTML page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Target TestBench" in response.text
