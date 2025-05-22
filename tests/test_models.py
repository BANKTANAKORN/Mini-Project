import pytest
from app import create_app, db
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

def test_user_model(session):
    user = User(name="John Doe", email="john@example.com", department="Engineering")
    session.add(user)
    session.commit()

    assert user.id is not None
    assert user.name == "John Doe"

def test_room_model(session):
    room = Room(room_name="Room A", floor="1", capacity=10)
    session.add(room)
    session.commit()

    assert room.id is not None
    assert room.room_name == "Room A"

def test_booking_model(session):
    user = User(name="Jane", email="jane@example.com", department="HR")
    room = Room(room_name="Room B", floor="2", capacity=5)
    session.add_all([user, room])
    session.commit()

    start = datetime.utcnow()
    end = start + timedelta(hours=1)

    booking = Booking(user_id=user.id, room_id=room.id, start_time=start, end_time=end)
    session.add(booking)
    session.commit()

    assert booking.id is not None
    assert booking.user == user
    assert booking.room == room
