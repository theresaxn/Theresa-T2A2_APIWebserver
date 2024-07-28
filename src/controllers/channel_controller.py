from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from main import db
from utils import current_member, auth_as_admin, channel_exist
from models.server import Server
from models.channel import Channel, channel_schema, channels_schema

channel_bp = Blueprint("channel", __name__, url_prefix="/<int:server_id>/channel")

# View all channels - GET - route: /server/<int:server_id>/channel/all
@channel_bp.route("/all")
@jwt_required()
@current_member("server_id")
def view_all_channels(server_id):
    # Fetch server from database
    server = Server.query.get(server_id)
    # If server does not exist
    if not server:
        # Return response
        return {"error": f"server with id {server_id} not found"}, 404
    # Fetch channels from database
    channels = Channel.query.filter_by(server_id=server_id).all()
    # If no channel exists
    if not channels:
        # Return response
        return {"message": f"no channels created in server {server.server_name} yet"}, 200
    else:
        # Return response if successful
        return channels_schema.dump(channels)
    
# View one channel - GET - route: /server/<int:server_id>/channel/<int:channel_id>
@channel_bp.route("/<int:channel_id>")
@jwt_required()
@channel_exist("server_id", "channel_id")
@current_member("server_id")
def view_one_channel(server_id, channel_id):
    # Fetch channel from database
    channel = Channel.query.filter_by(server_id=server_id, channel_id=channel_id).first()
    # Return response 
    return channel_schema.dump(channel)
    
# Add channel - POST - route: /server/<int:server_id>/channel/create
@channel_bp.route("/create", methods=["POST"])
@jwt_required()
@current_member("server_id")
@auth_as_admin("server_id")
def create_channel(server_id):
    try:
        # Get data from body of request
        body_data = channel_schema.load(request.get_json())
        # Create instance of Channel model
        new_channel = Channel(
            channel_name = body_data.get("channel_name"),
            created_on = date.today(),
            creator_user_id = get_jwt_identity(),
            server_id = server_id
        )
        # Add and commit to database
        db.session.add(new_channel)
        db.session.commit()
        # Return response
        return channel_schema.dump(new_channel), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is required"}, 409

# Update channel - PATCH, PUT - route: /server/<int:server_id>/channel/update/<int:channel_id>
@channel_bp.route("/update/<int:channel_id>", methods=["PUT", "PATCH"])
@jwt_required()
@channel_exist("server_id", "channel_id")
@current_member("server_id")
@auth_as_admin("server_id")
def update_channel(server_id, channel_id):
    # Get data from body of request
    body_data = channel_schema.load(request.get_json())
    # Fetch channel from database
    channel = Channel.query.get(channel_id)
    # Update fields
    channel.channel_name = body_data.get("channel_name") or channel.channel_name
    # Commit to database
    db.session.commit()
    # Return response
    return channel_schema.dump(channel)

# Delete channel - DELETE - route: /server/<int:server_id>/channel/delete/<int:channel_id>
@channel_bp.route("/delete/<int:channel_id>", methods=["DELETE"])
@jwt_required()
@channel_exist("server_id", "channel_id")
@current_member("server_id")
@auth_as_admin("server_id")
def delete_channel(server_id, channel_id):
    # Fetch channel from database
    channel = Channel.query.get(channel_id)
    # Delete and commit to database
    db.session.delete(channel)
    db.session.commit()
    # Return response
    return {"message": f"channel {channel.channel_name} has been deleted from server {channel.server.server_name}"}