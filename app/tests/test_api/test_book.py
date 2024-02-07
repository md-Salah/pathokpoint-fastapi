from fastapi.testclient import TestClient
from sqlmodel import Session
from app.main import app


def test_create_book(session: Session, client: TestClient):
    client = TestClient(app)
    payload = {
            "email": "testuser@gmail.com",
            "password": "testPassword2235#",
            "phone_number": "+8801311701123",
            "first_name": "test",
            "last_name": "user1"
        }
    response = client.post(
        "/book", json=payload
    )
    data = response.json()

    assert response.status_code == 201
    assert payload.items() <= data.items()
    assert data['role'] == "customer"
    assert data['token'] is not None
    
    

