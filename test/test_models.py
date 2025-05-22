# test/test_models.py
import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, User, Room, Booking
from app import create_app
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def setup_db(app):
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

def test_user_model(setup_db):
    user = User(name="Test User", email="test@example.com", department="IT")
    db.session.add(user)
    db.session.commit()
    assert User.query.filter_by(email="test@example.com").first() is not None

def test_room_model(setup_db):
    room = Room(room_name="Room A", floor="1st Floor", capacity=10)
    db.session.add(room)
    db.session.commit()
    assert Room.query.filter_by(room_name="Room A").first().capacity == 10

def test_booking_model_constraints(setup_db):
    user = User(name="U", email="u@example.com", department="IT")
    room = Room(room_name="Room B", floor="2nd Floor", capacity=5)
    db.session.add_all([user, room])
    db.session.commit()

    start = datetime.utcnow() + timedelta(hours=1)
    end = start + timedelta(hours=1)

    booking = Booking(user_id=user.id, room_id=room.id, start_time=start, end_time=end)
    db.session.add(booking)
    db.session.commit()

    assert Booking.query.first().user_id == user.id
