from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from main import db
from utils import current_member, auth_as_admin, member_exist
from models.server import Server
from models.user import User
from models.server_member import ServerMember, server_member_schema, server_members_schema

member_bp = Blueprint("member", __name__, url_prefix="/<int:server_id>/member")

# View all members - GET - server/<int:server_id>/member/all
@member_bp.route("/all")
@jwt_required()
@current_member("server_id")
def view_all_members(server_id):
    server_members = ServerMember.query.filter_by(server_id=server_id).all()
    return server_members_schema.dump(server_members)

# View one member - GET - server/<int:server_id>/member/<int:member_id>
@member_bp.route("/<int:member_id>")
@jwt_required()
@current_member("server_id")
@member_exist("server_id", "member_id")
def view_one_member(server_id, member_id):
    server_member = ServerMember.query.filter_by(server_id=server_id, member_id=member_id).first()
    return server_member_schema.dump(server_member)

# Join server - POST - server/<int:server_id>/member/join
@member_bp.route("/join", methods=["POST"])
@jwt_required()
def join_server(server_id):
    server = Server.query.get(server_id)
    if not server:
        return {"error": f"server with id {server_id} not found"}, 404
    else:
        server_member = ServerMember.query.filter_by(server=server, user_id=get_jwt_identity()).first()
        if server_member:
            return {"error": f"user is already a member of server {server.server_name}"}, 400
        new_member = ServerMember(
            joined_on = date.today(),
            server = server,
            user_id = get_jwt_identity()
        )
        db.session.add(new_member)
        db.session.commit()
        return server_member_schema.dump(new_member)

# Add member - POST - server/<int:server_id>/member/add/<int:user_id>
@member_bp.route("/add/<int:user_id>", methods=["POST"])
@jwt_required()
@current_member("server_id")
@auth_as_admin("server_id")
def add_member(server_id, user_id):
    user = User.query.get(user_id)
    server = Server.query.get(server_id)
    if not user:
        return {"error": f"user with id {user_id} not found"}, 404
    existing_member = ServerMember.query.filter_by(server=server, user_id=user_id).first()
    if existing_member:
        return {"error": f"user {user.username} is already a member of server {server.server_name}"}, 400
    else:
        new_member = ServerMember(
            joined_on = date.today(),
            server = server,
            user_id = user_id
        )
        db.session.add(new_member)
        db.session.commit()
    return server_member_schema.dump(new_member)

# Update member - PUT, PATCH - server/<int:server_id>/member/update/<int:member_id>
@member_bp.route("/update/<int:member_id>", methods=["PUT", "PATCH"])
@jwt_required()
@member_exist("server_id", "member_id")
@current_member("server_id")
@auth_as_admin("server_id")
def update_member(server_id, member_id):
    body_data = request.get_json()
    server_member = ServerMember.query.get(member_id)
    if server_member.user_id == server_member.server.creator_user_id:
        return {"error": f"user {server_member.user.username} cannot be updated or deleted"}
    else:
        server_member.is_admin = body_data.get("is_admin") or server_member.is_admin
        return server_member_schema.dump(server_member)

# Delete member - DELETE - server/<int:server_id>/member/delete/<int:member_id>
@member_bp.route("/delete/<int:member_id>", methods=["DELETE"])
@jwt_required()
@member_exist("server_id", "member_id")
@current_member("server_id")
@auth_as_admin("server_id")
def delete_member(server_id, member_id):
    server_member = ServerMember.query.get(member_id)
    if server_member.user_id == server_member.server.creator_user_id:
        return {"error": f"user {server_member.user.username} cannot be updated or deleted"}
    db.session.delete(server_member)
    db.session.commit()
    return {"message": f"member {server_member.user.username} has been deleted from server {server_member.server.server_name}"}