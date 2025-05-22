import pytest
import json
from app import create_app, db
from app.models import User, Room, Booking

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"  # DB ชั่วคราวใน RAM
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_user(client):
    response = client.post('/api/users', json={
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == "John Doe"
    assert data['email'] == "john@example.com"

def test_get_user(client):
    # สร้าง user ก่อน
    client.post('/api/users', json={
        "name": "Alice",
        "email": "alice@example.com",
        "department": "HR"
    })
    response = client.get('/api/users/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "Alice"
    assert data['department'] == "HR"

def test_create_room(client):
    response = client.post('/api/rooms', json={
        "room_name": "Room A",
        "floor": "3rd",
        "capacity": 10
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['room_name'] == "Room A"

def test_list_rooms(client):
    client.post('/api/rooms', json={
        "room_name": "Room B",
        "floor": "1st",
        "capacity": 5
    })
    response = client.get('/api/rooms')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1

def test_create_booking(client):
    # สร้าง user และ room ก่อน
    client.post('/api/users', json={
        "name": "Bob",
        "email": "bob@example.com",
        "department": "Sales"
    })
    client.post('/api/rooms', json={
        "room_name": "Room C",
        "floor": "2nd",
        "capacity": 8
    })

    booking_data = {
        "user_id": 1,
        "room_id": 1,
        "start_time": "2030-01-01T10:00:00+00:00",
        "end_time": "2030-01-01T11:00:00+00:00"
    }
    response = client.post('/api/bookings', json=booking_data)
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data

def test_create_booking_overlap(client):
    # สร้าง user และ room ก่อน
    client.post('/api/users', json={
        "name": "Cathy",
        "email": "cathy@example.com",
        "department": "Marketing"
    })
    client.post('/api/rooms', json={
        "room_name": "Room D",
        "floor": "4th",
        "capacity": 12
    })

    booking1 = {
        "user_id": 1,
        "room_id": 1,
        "start_time": "2030-02-01T09:00:00+00:00",
        "end_time": "2030-02-01T10:00:00+00:00"
    }
    client.post('/api/bookings', json=booking1)

    # ลองจองซ้ำเวลาทับซ้อน
    booking2 = {
        "user_id": 1,
        "room_id": 1,
        "start_time": "2030-02-01T09:30:00+00:00",
        "end_time": "2030-02-01T10:30:00+00:00"
    }
    response = client.post('/api/bookings', json=booking2)
    assert response.status_code == 400
    data = response.get_json()
    assert "already booked" in data['error']

def test_get_bookings(client):
    # สร้าง user, room, booking
    client.post('/api/users', json={
        "name": "David",
        "email": "david@example.com",
        "department": "Tech"
    })
    client.post('/api/rooms', json={
        "room_name": "Room E",
        "floor": "5th",
        "capacity": 15
    })
    client.post('/api/bookings', json={
        "user_id": 1,
        "room_id": 1,
        "start_time": "2030-03-01T08:00:00+00:00",
        "end_time": "2030-03-01T09:00:00+00:00"
    })

    response = client.get('/api/bookings?room_id=1&date=2030-03-01')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1

def test_delete_booking(client):
    # สร้าง user, room, booking
    client.post('/api/users', json={
        "name": "Eve",
        "email": "eve@example.com",
        "department": "Admin"
    })
    client.post('/api/rooms', json={
        "room_name": "Room F",
        "floor": "6th",
        "capacity": 20
    })
    client.post('/api/bookings', json={
        "user_id": 1,
        "room_id": 1,
        "start_time": "2030-04-01T14:00:00+00:00",
        "end_time": "2030-04-01T15:00:00+00:00"
    })

    # ลบการจอง
    response = client.delete('/api/bookings/1')
    assert response.status_code == 200
    data = response.get_json()
    assert "deleted" in data["message"]

    # ลองลบอีกครั้ง จะต้อง 404
    response2 = client.delete('/api/bookings/1')
    assert response2.status_code == 404

