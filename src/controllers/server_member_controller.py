from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from main import db
from utils import auth_member_action
from models.server import Server
from models.user import User
from models.server_member import ServerMember, server_member_schema, server_members_schema

member_bp = Blueprint("member", __name__, url_prefix="/member")

# View all server members - GET - server/member/<int:server_id>/all
@member_bp.route("/<int:server_id>/all")
@jwt_required()
def view_all_members(server_id):
    server = Server.query.get(server_id)
    if not server:
        return {"error": f"server with id {server_id} not found"}, 404
    server_members = ServerMember.query.filter_by(server_id=server_id).all()
    return server_members_schema.dump(server_members)

# View one server member - GET - server/member/<int:member_id>
@member_bp.route("/<int:member_id>")
@jwt_required()
def view_one_member(member_id):
    server_member = ServerMember.query.get(member_id)
    if not server_member:
        return {"error": f"server member with id {member_id} not found"}, 404
    return server_member_schema.dump(server_member)

# Join server - POST - server/member/<int:server_id>/join
@member_bp.route("/<int:server_id>/join", methods=["POST"])
@jwt_required()
def join_server(server_id):
    server = Server.query.get(server_id)
    if not server:
        return {"error": f"server with id {server_id} not found"}, 404
    else:
        stmt = db.select(ServerMember).filter_by(server=server, user_id=get_jwt_identity())
        server_member = db.session.scalar(stmt)
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

# Add member - POST - server/member/<int:server_id>/add/<int:user_id>
@member_bp.route("/<int:server_id>/add/<int:user_id>", methods=["POST"])
@jwt_required()
def add_member(server_id, user_id):
    user = User.query.get(user_id)
    server = Server.query.get(server_id)
    if not user:
        return {"error": f"user with id {user_id} not found"}, 404
    if not server:
        return {"error": f"server with id {server_id} not found"}, 404
    else:
        stmt = db.select(ServerMember).filter_by(server=server, user_id=get_jwt_identity())
        server_member = db.session.scalar(stmt)
        if not server_member or not server_member.is_admin:
            return {"error": "user not authorised to perform this action"}, 403
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
       
# Update if admin - PUT, PATCH - server/member/update/<int:member_id>
@member_bp.route("/update/<int:member_id>", methods=["PUT", "PATCH"])
@jwt_required()
@auth_member_action("member_id")
def update_member(member_id):
    body_data = request.get_json()
    server_member = ServerMember.query.get(member_id)
    server_member.is_admin = body_data.get("is_admin") or server_member.is_admin
    return server_member_schema.dump(server_member)

# Delete server member - DELETE - server/member/delete/<int:member_id>
@member_bp.route("delete/<int:member_id>", methods=["DELETE"])
@jwt_required()
@auth_member_action("member_id")
def delete_member(member_id):
    stmt = db.select(ServerMember).filter_by(member_id=member_id)
    member = db.session.scalar(stmt)
    db.session.delete(member)
    db.session.commit()
    return {"message": f"member {member.user.username} has been deleted from server {member.server.server_name}"}