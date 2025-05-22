import pytest
from datetime import datetime, timedelta
from services import create_user, get_user, create_room, list_rooms, create_booking, get_bookings
from models import db, User, Room, Booking

@pytest.fixture
def setup_db(app):
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

def test_create_and_get_user(setup_db):
    data = {"name": "User1", "email": "user1@example.com", "department": "Sales"}
    user = create_user(data)
    fetched = get_user(user.id)
    assert fetched.email == data['email']

def test_create_room_and_list(setup_db):
    data = {"room_name": "Conference", "floor": "3rd", "capacity": 20}
    create_room(data)
    rooms = list_rooms()
    assert any(r.room_name == "Conference" for r in rooms)

def test_create_booking_success(setup_db):
    u = create_user({"name":"U","email":"u@ex.com","department":"IT"})
    r = create_room({"room_name":"R","floor":"1","capacity":5})

    start = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    end = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    data = {"user_id": u.id, "room_id": r.id, "start_time": start, "end_time": end}
    
    booking = create_booking(data)
    assert booking.room_id == r.id

def test_create_booking_overlap_raises(setup_db):
    u = create_user({"name":"U","email":"u@ex.com","department":"IT"})
    r = create_room({"room_name":"R","floor":"1","capacity":5})

    start = datetime.utcnow() + timedelta(hours=1)
    end = start + timedelta(hours=2)

    # create first booking
    create_booking({
        "user_id": u.id, 
        "room_id": r.id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })

    # try overlapping booking
    with pytest.raises(ValueError) as excinfo:
        create_booking({
            "user_id": u.id,
            "room_id": r.id,
            "start_time": (start + timedelta(minutes=30)).isoformat(),
            "end_time": (end + timedelta(minutes=30)).isoformat()
        })
    assert "already booked" in str(excinfo.value)

def test_create_booking_in_past_raises(setup_db):
    u = create_user({"name":"U","email":"u@ex.com","department":"IT"})
    r = create_room({"room_name":"R","floor":"1","capacity":5})

    past_start = (datetime.utcnow() - timedelta(days=1)).isoformat()
    past_end = (datetime.utcnow() - timedelta(hours=23)).isoformat()

    with pytest.raises(ValueError) as excinfo:
        create_booking({
            "user_id": u.id,
            "room_id": r.id,
            "start_time": past_start,
            "end_time": past_end
        })
    assert "past" in str(excinfo.value)

def test_get_bookings_by_room_and_date(setup_db):
    u = create_user({"name":"U","email":"u@ex.com","department":"IT"})
    r = create_room({"room_name":"R","floor":"1","capacity":5})

    start = datetime.utcnow() + timedelta(hours=1)
    end = start + timedelta(hours=1)

    create_booking({
        "user_id": u.id,
        "room_id": r.id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    })

    bookings = get_bookings(r.id, start.date().isoformat())
    assert len(bookings) == 1
