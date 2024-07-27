from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from main import db
from utils import current_member, auth_as_admin, channel_exist
from models.server import Server
from models.channel import Channel, channel_schema, channels_schema

channel_bp = Blueprint("channel", __name__, url_prefix="/<int:server_id>/channel")

# View all channels - GET - server/<int:server_id>/channel/all
@channel_bp.route("/all")
@jwt_required()
@current_member("server_id")
def view_all_channels(server_id):
    server = Server.query.get(server_id)
    if not server:
        return {"error": f"server with id {server_id} not found"}, 404
    channels = Channel.query.filter_by(server_id=server_id).all()
    if not channels:
        return {"message": f"no channels created in server {server.server_name} yet"}, 200
    else:
        return channels_schema.dump(channels)
    
# View one channel - GET - server/<int:server_id>/channel/<int:channel_id>
@channel_bp.route("/<int:channel_id>")
@jwt_required()
@channel_exist("server_id", "channel_id")
@current_member("server_id")
def view_one_channel(server_id, channel_id):
    channel = Channel.query.filter_by(server_id=server_id, channel_id=channel_id).first()
    return channel_schema.dump(channel)
    
# Add channel - POST - server/<int:server_id>/channel/create
@channel_bp.route("/create", methods=["POST"])
@jwt_required()
@current_member("server_id")
@auth_as_admin("server_id")
def create_channel(server_id):
    body_data = channel_schema.load(request.get_json())
    new_channel = Channel(
        channel_name = body_data.get("channel_name"),
        created_on = date.today(),
        creator_user_id = get_jwt_identity(),
        server_id = server_id
    )
    db.session.add(new_channel)
    db.session.commit()
    return channel_schema.dump(new_channel)

# Update channel - PATCH, PUT - server/<int:server_id>/channel/update/<int:channel_id>
@channel_bp.route("/update/<int:channel_id>", methods=["PUT", "PATCH"])
@jwt_required()
@channel_exist("server_id", "channel_id")
@current_member("server_id")
@auth_as_admin("server_id")
def update_channel(server_id, channel_id):
    body_data = channel_schema.load(request.get_json())
    channel = Channel.query.get(channel_id)
    channel.channel_name = body_data.get("channel_name") or channel.channel_name
    db.session.commit()
    return channel_schema.dump(channel)

# Delete channel - DELETE - server/<int:server_id>/channel/delete/<int:channel_id>
@channel_bp.route("/delete/<int:channel_id>", methods=["DELETE"])
@jwt_required()
@channel_exist("server_id", "channel_id")
@current_member("server_id")
@auth_as_admin("server_id")
def delete_channel(server_id, channel_id):
    channel = Channel.query.get(channel_id)
    db.session.delete(channel)
    db.session.commit()
    return {"message": f"channel {channel.channel_name} has been deleted from server {channel.server.server_name}"}