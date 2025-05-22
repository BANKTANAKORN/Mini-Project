from app import db
from app.models import User, Room, Booking
from datetime import datetime, timezone

def create_user(data):
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user

def get_user(user_id):
    return User.query.get(user_id)

def create_room(data):
    room = Room(**data)
    db.session.add(room)
    db.session.commit()
    return room

def list_rooms():
    return Room.query.all()

def create_booking(data):
    start = datetime.fromisoformat(data['start_time'])
    end = datetime.fromisoformat(data['end_time'])

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    if start >= end:
        raise ValueError("End time must be after start time")

    now = datetime.now(timezone.utc)
    if start < now:
        raise ValueError("Cannot book room in the past")

    # ✅ ตรวจสอบว่าผู้ใช้และห้องมีอยู่จริง
    user = User.query.get(data['user_id'])
    if not user:
        raise ValueError(f"User ID {data['user_id']} not found")

    room = Room.query.get(data['room_id'])
    if not room:
        raise ValueError(f"Room ID {data['room_id']} not found")

    # ✅ ตรวจสอบการจองซ้อน
    overlapping = Booking.query.filter(
        Booking.room_id == data['room_id'],
        Booking.start_time < end,
        Booking.end_time > start
    ).all()

    if overlapping:
        raise ValueError("Room is already booked at that time")

    booking = Booking(
        user_id=data['user_id'],
        room_id=data['room_id'],
        start_time=start,
        end_time=end
    )
    db.session.add(booking)
    db.session.commit()
    return booking


def get_bookings(room_id, date_str):
    if not room_id or not date_str:
        return []

    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    bookings = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.start_time >= datetime.combine(date, datetime.min.time()),
        Booking.start_time <= datetime.combine(date, datetime.max.time())
    ).all()
    return bookings

def delete_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        raise ValueError("Booking not found")
    db.session.delete(booking)
    db.session.commit()

