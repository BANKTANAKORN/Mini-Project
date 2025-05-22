from flask import Blueprint, request, jsonify
from services import *
from models import db

api = Blueprint('api', __name__)

@api.route('/api/users', methods=['POST'])
def create_user_route():
    data = request.json
    try:
        user = create_user(data)
        return jsonify({"id": user.id, "name": user.name, "email": user.email, "department": user.department}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_route(user_id):
    user = get_user(user_id)
    if user:
        return jsonify({"id": user.id, "name": user.name, "email": user.email, "department": user.department})
    return jsonify({"error": "User not found"}), 404

@api.route('/api/rooms', methods=['POST'])
def create_room_route():
    data = request.json
    try:
        room = create_room(data)
        return jsonify({"id": room.id, "room_name": room.room_name}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api.route('/api/rooms', methods=['GET'])
def get_rooms():
    rooms = list_rooms()
    return jsonify([{"id": r.id, "room_name": r.room_name} for r in rooms])


@api.route('/api/bookings', methods=['POST'])
def book_room():
    data = request.json
    required_fields = ['user_id', 'room_id', 'start_time', 'end_time']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    try:
        booking = create_booking(data)
        return jsonify({"id": booking.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api.route('/api/bookings', methods=['GET'])
def get_booking_by_room_date():
    room_id = request.args.get('room_id')
    date = request.args.get('date')

    if not room_id or not date:
        return jsonify({"error": "Missing room_id or date parameter"}), 400

    try:
        room_id = int(room_id)
    except ValueError:
        return jsonify({"error": "Invalid room_id parameter"}), 400

    try:
        bookings = get_bookings(room_id, date)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if not bookings:
        return jsonify({"message": "No bookings found for this room and date"}), 404

    return jsonify([
        {
            "id": b.id,
            "user_id": b.user_id,
            "start_time": b.start_time.isoformat(),
            "end_time": b.end_time.isoformat()
        } for b in bookings
    ])


@api.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking_route(booking_id):
    try:
        delete_booking(booking_id)
        return jsonify({"message": "Booking deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
