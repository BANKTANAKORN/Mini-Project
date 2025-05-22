import pytest
from app import create_app, db
from app.services import create_user, get_user, create_room, list_rooms, create_booking, get_bookings, delete_booking
from app.models import User, Room, Booking
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session(app):
    return db.session

def test_create_and_get_user(session):
    user_data = {"name": "Alice", "email": "alice@example.com", "department": "Sales"}
    user = create_user(user_data)
    fetched_user = get_user(user.id)

    assert fetched_user is not None
    assert fetched_user.email == "alice@example.com"

def test_create_and_list_rooms(session):
    room_data = {"room_name": "Conference Room", "floor": "3", "capacity": 20}
    create_room(room_data)
    rooms = list_rooms()
    assert len(rooms) == 1
    assert rooms[0].room_name == "Conference Room"

def test_create_booking(session):
    user = create_user({"name": "Bob", "email": "bob@example.com", "department": "IT"})
    room = create_room({"room_name": "Room C", "floor": "1", "capacity": 10})
    start = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    end = (datetime.utcnow() + timedelta(hours=2)).isoformat()

    booking_data = {
        "user_id": user.id,
        "room_id": room.id,
        "start_time": start,
        "end_time": end
    }

    booking = create_booking(booking_data)
    assert booking is not None
    assert booking.user_id == user.id
    assert booking.room_id == room.id

def test_create_booking_overlap(session):
    user = create_user({"name": "Charlie", "email": "charlie@example.com", "department": "Finance"})
    room = create_room({"room_name": "Room D", "floor": "2", "capacity": 8})
    start = datetime.utcnow() + timedelta(hours=1)
    end = start + timedelta(hours=2)

    booking1 = create_booking({
        "user_id": user.id,
        "room_id": room.id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })

    # พยายามจองช่วงเวลาซ้อนกัน
    with pytest.raises(ValueError, match="Room is already booked at that time"):
        create_booking({
            "user_id": user.id,
            "room_id": room.id,
            "start_time": (start + timedelta(minutes=30)).isoformat(),
            "end_time": (end + timedelta(minutes=30)).isoformat()
        })

def test_get_bookings(session):
    user = create_user({"name": "Dana", "email": "dana@example.com", "department": "Marketing"})
    room = create_room({"room_name": "Room E", "floor": "1", "capacity": 5})
    date = (datetime.utcnow() + timedelta(days=1)).date()  # เลื่อนไปวันถัดไป

    start = datetime.combine(date, datetime.min.time()) + timedelta(hours=9)
    end = start + timedelta(hours=1)

    create_booking({
        "user_id": user.id,
        "room_id": room.id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })

    bookings = get_bookings(room.id, date.isoformat())
    assert len(bookings) == 1

def test_delete_booking(session):
    user = create_user({"name": "Eve", "email": "eve@example.com", "department": "HR"})
    room = create_room({"room_name": "Room F", "floor": "2", "capacity": 12})

    start = datetime.utcnow() + timedelta(hours=1)
    end = start + timedelta(hours=2)

    booking = create_booking({
        "user_id": user.id,
        "room_id": room.id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })

    delete_booking(booking.id)

    deleted = Booking.query.get(booking.id)
    assert deleted is None
