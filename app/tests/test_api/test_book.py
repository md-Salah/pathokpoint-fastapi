from fastapi.testclient import TestClient

def create_book(payload: dict, client: TestClient):
    return client.post("/book", json=payload)

def test_get_book_by_id(client: TestClient):
    payload = {
        "name": "Test Book",
        "regular_price": 100
    }
    response = create_book(payload, client)
    data = response.json()
    response = client.get(f"/book/id/{data['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Book"

def test_update_book(client: TestClient):
    payload = {
        "name": "Test Book",
        "regular_price": 100
    }
    response = create_book(payload, client)
    data = response.json()
    payload = {
        "name": "Updated Book",
    }
    response = client.patch(f"/book/{data['id']}", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Updated Book"
    assert data["regular_price"] == 100

def test_delete_book(client: TestClient):
    payload = {
        "name": "Test Delete Book",
        "regular_price": 100
    }
    response = create_book(payload, client)
    data = response.json()
    response = client.delete(f"/book/{data['id']}")
    data = response.json()
    assert response.status_code == 200
    response = client.get(f"/book/id/{data['id']}")
    assert response.status_code == 404

def test_get_book_by_slug(client: TestClient):
    payload = {
        "name": "Test Book by Slug",
        "regular_price": 100
    }
    response = create_book(payload, client)
    data = response.json()
    response = client.get(f"/book/slug/{data['slug']}")
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Test Book by Slug"  
      

def test_get_all_books(client: TestClient):
    payload = {
        "name": "Test Book",
        "regular_price": 100
    }
    create_book(payload, client)
    response = client.get("/books")
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Book"
    
    
def test_create_book(client: TestClient):
    # Test slug is generated
    payload = {
        "name": "Test Book",
        "regular_price": 100
    }
    response = client.post("/book", json=payload)
    data = response.json()
    assert response.status_code == 201
    assert data["name"] == "Test Book"
    assert data['slug'].startswith('test-book')
    
