import requests

def test_end_to_end():
    response = requests.get("http://localhost:8000")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to RAG Web UI API"}
