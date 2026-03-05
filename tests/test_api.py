from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.apimain import app

client = TestClient(app)


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_recommend_invalid_user():
    response = client.post("/recommend", json={"user_id": -1})
    assert response.status_code == 400


def test_recommend_out_of_range():
    response = client.post("/recommend", json={"user_id": 999999})
    assert response.status_code == 400


@patch("api.inference.get_top10")
def test_recommend_valid(mock_get_top10):
    mock_get_top10.return_value = ["The Godfather", "Pulp Fiction"]
    response = client.post("/recommend", json={"user_id": 0})
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) == 2