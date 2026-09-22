from app import app


def test_hello():
    client = app.test_client()
    response = client.get("/hello")
    assert response.status_code == 200


def test_create_event_valid():
    client = app.test_client()
    response = client.post("/events", json={
        "type": "purchase",
        "value": 90,
        "timestamp": "2026-08-09T11:11:11",
        "source": "mobile"
    })
    assert response.status_code == 201


def test_create_event_missing_fields():
    client = app.test_client()
    response = client.post("/events", json={"value": 20})
    assert response.status_code == 400


def test_create_event_invalid_value_type():
    client = app.test_client()
    response = client.post("/events", json={
        "type": "click",
        "value": "ninety",
        "timestamp": "2026-08-09T11:11:11",
        "source": "web"
    })
    assert response.status_code == 400
