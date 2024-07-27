import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from main import db
from utils import current_member_check, message_exist, channel_message_exist
from models.user import User
from models.message import Message, message_schema, messages_schema

message_bp = Blueprint("message", __name__, url_prefix="/message")
message_user_bp = Blueprint("message_user", __name__, url_prefix="/user/message")
message_channel_bp = Blueprint("message_channel", __name__, url_prefix="/channel/<int:channel_id>/message")

# View all direct messages received - GET - route: /user/message/all
@message_user_bp.route("/all")
@jwt_required()
def view_all_direct_messages():
    messages = Message.query.filter_by(receiver_user_id=get_jwt_identity()).order_by(Message.timestamp.desc()).all()
    if not messages:
        return {"message": "no messages sent to user yet"}, 200
    return messages_schema.dump(messages)

# View all channel messages - GET - route: /channel/<int:channel_id>/message/all
@message_channel_bp.route("/all")
@jwt_required()
@current_member_check("channel_id")
def view_all_channel_messages(channel_id):
    messages = Message.query.filter_by(channel_id=channel_id).all()
    if not messages:
        return {"message": f"no messages posted to {messages.channel.channel_name} yet"}, 200
    return messages_schema.dump(messages)

# View one channel messages - GET - route: /channel/<int:channel_id>/message/<int:message_id>
@message_channel_bp.route("/<int:message_id>")
@jwt_required()
@current_member_check("channel_id")
@channel_message_exist("channel_id", "message_id")
def view_one_channel_message(channel_id, message_id):
    message = Message.query.filter_by(channel_id=channel_id, message_id=message_id).first()
    return message_schema.dump(message)

# Send direct message - POST - route: /user/message/send/<int:user_id>
@message_user_bp.route("/send/<int:user_id>", methods=["POST"])
@jwt_required()
def send_direct_message(user_id):
    try:
        body_data = message_schema.load(request.get_json())
        user = User.query.get(user_id)
        if not user:
            return {"error": f"user with id {user_id} not found"}, 404
        else:
            new_message = Message(
                content = body_data.get("content"),
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                sender_user_id = get_jwt_identity(),
                receiver_user_id = user_id
            )
        db.session.add(new_message)
        db.session.commit()
        return message_schema.dump(new_message)
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is required"}, 409

# Post channel message - POST - route: /channel/<int:channel_id>/message/post
@message_channel_bp.route("/post", methods=["POST"])
@jwt_required()
@current_member_check("channel_id")
def add_channel_message(channel_id):
    try:
        body_data = message_schema.load(request.get_json())
        new_message = Message(
            title = body_data.get("title"),
            content = body_data.get("content"),
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            channel_id = channel_id,
            sender_user_id = get_jwt_identity()
        )
        db.session.add(new_message)
        db.session.commit()
        return message_schema.dump(new_message)
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is required"}, 409

# Update message - PUT, PATCH - route: /message/update/<int:message_id>
@message_bp.route("/update/<int:message_id>", methods=["PUT", "PATCH"])
@jwt_required()
@message_exist("message_id")
def update_message(message_id):
    body_data = message_schema.load(request.get_json())
    message = Message.query.get(message_id)
    message.content = body_data.get("content") or message.content
    message.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if message.channel != None:
        message.title = body_data.get("title") or message.title
        db.session.commit()
        return message_schema.dump(message)
    else:
        db.session.commit()
        return message_schema.dump(message)
    
# Delete message - DELETE - route: /message/update/<int:message_id>
@message_bp.route("/delete/<int:message_id>", methods=["DELETE"])
@jwt_required()
@message_exist("message_id")
def delete_message(message_id):
    message = Message.query.get(message_id)
    db.session.delete(message)
    db.session.commit()
    return {"message": f"message with id {message_id} has been deleted"}



