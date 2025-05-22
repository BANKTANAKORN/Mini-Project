import pytest
from app import app as flask_app
from models import db
from datetime import datetime, timedelta

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.drop_all()

def test_create_user_api(client):
    res = client.post('/api/users', json={
        "name": "API User",
        "email": "apiuser@example.com",
        "department": "HR"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "id" in data

def test_get_user_api(client):
    # Create user first
    res = client.post('/api/users', json={
        "name": "API User 2",
        "email": "apiuser2@example.com",
        "department": "Finance"
    })
    uid = res.get_json()['id']

    res = client.get(f'/api/users/{uid}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['email'] == "apiuser2@example.com"

def test_create_room_api(client):
    res = client.post('/api/rooms', json={
        "room_name": "API Room",
        "floor": "Ground",
        "capacity": 15
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "id" in data

def test_list_rooms_api(client):
    # Create room first
    client.post('/api/rooms', json={
        "room_name": "API Room 2",
        "floor": "1st",
        "capacity": 10
    })

    res = client.get('/api/rooms')
    assert res.status_code == 200
    data = res.get_json()
    assert any(r['room_name'] == "API Room 2" for r in data)

def test_create_booking_api_success(client):
    # Create user & room first
    u_res = client.post('/api/users', json={"name": "BUser", "email": "buser@example.com", "department": "IT"})
    r_res = client.post('/api/rooms', json={"room_name": "BRoom", "floor": "2nd", "capacity": 5})
    u_id = u_res.get_json()['id']
    r_id = r_res.get_json()['id']

    start = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    end = (datetime.utcnow() + timedelta(hours=2)).isoformat()

    res = client.post('/api/bookings', json={
        "user_id": u_id,
        "room_id": r_id,
        "start_time": start,
        "end_time": end
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "id" in data

def test_create_booking_api_overlap(client):
    u_res = client.post('/api/users', json={"name": "BUser2", "email": "buser2@example.com", "department": "IT"})
    r_res = client.post('/api/rooms', json={"room_name": "BRoom2", "floor": "2nd", "capacity": 5})
    u_id = u_res.get_json()['id']
    r_id = r_res.get_json()['id']

    start = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    end = (datetime.utcnow() + timedelta(hours=2)).isoformat()

    client.post('/api/bookings', json={
        "user_id": u_id,
        "room_id": r_id,
        "start_time": start,
        "end_time": end
    })

    # Try overlap booking
    res = client.post('/api/bookings', json={
        "user_id": u_id,
        "room_id": r_id,
        "start_time": (datetime.utcnow() + timedelta(hours=1, minutes=30)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=2, minutes=30)).isoformat()
    })

    assert res.status_code == 400
    data = res.get_json()
    assert "already booked" in data['error']

def test_create_booking_api_past(client):
    u_res = client.post('/api/users', json={"name": "BUser3", "email": "buser3@example.com", "department": "IT"})
    r_res = client.post('/api/rooms', json={"room_name": "BRoom3", "floor": "2nd", "capacity": 5})
    u_id = u_res.get_json()['id']
    r_id = r_res.get_json()['id']

    past_start = (datetime.utcnow() - timedelta(days=1)).isoformat()
    past_end = (datetime.utcnow() - timedelta(hours=23)).isoformat()

    res = client.post('/api/bookings', json={
        "user_id": u_id,
        "room_id": r_id,
        "start_time": past_start,
        "end_time": past_end
    })
    assert res.status_code == 400
    data = res.get_json()
    assert "past" in data['error']
