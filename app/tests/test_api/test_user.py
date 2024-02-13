from fastapi.testclient import TestClient
from app.main import app


# def test_user_signup_with_all_value(session: Session, client: TestClient):
#     client = TestClient(app)
#     payload = {
#             "email": "testuser@gmail.com",
#             "password": "testPassword2235#",
#             "phone_number": "+8801311701123",
#             "first_name": "test",
#             "last_name": "user1"
#         }
#     response = client.post(
#         "/signup", json=payload
#     )
#     data = response.json()

#     payload.pop('password')
#     assert response.status_code == 201
#     assert payload.items() <= data.items()
#     assert data['role'] == "customer"
#     assert data['token'] is not None
    
    
# def test_user_with_email_password(session: Session, client: TestClient):
#     client = TestClient(app)
#     payload = {
#             "email": "testuser2@gmail.com",
#             "password": "testPassword2235#",
#     }
#     response = client.post(
#         "/signup", json=payload
#     )
#     data = response.json()
#     assert response.status_code == 201
#     assert data['role'] == "customer"
#     assert data['token'] is not None
    

# def test_user_with_invalid_phone_number(session: Session, client: TestClient):
#     client = TestClient(app)
#     payload = {
#             "email": "testuser2@gmail.com",
#             "password": "testPassword2235#",
#             "phone_number": "+893",
#     }
#     response = client.post(
#         "/signup", json=payload
#     )
#     data = response.json()
#     assert response.status_code == 422
#     assert data['detail'][0]['loc'][1] == 'phone_number'
#     assert data['detail'][0]['msg'] == 'ensure this value has at least 8 characters'
    
