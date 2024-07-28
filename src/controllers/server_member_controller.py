from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from main import db
from utils import current_member, auth_as_admin, member_exist
from models.server import Server
from models.user import User
from models.server_member import ServerMember, server_member_schema, server_members_schema

member_bp = Blueprint("member", __name__, url_prefix="/<int:server_id>/member")

# View all members - GET - route: /server/<int:server_id>/member/all
@member_bp.route("/all")
@jwt_required()
@current_member("server_id")
def view_all_members(server_id):
    # Fetch server members from database
    server_members = ServerMember.query.filter_by(server_id=server_id).all()
    # Return response
    return server_members_schema.dump(server_members)

# View one member - GET - route: /server/<int:server_id>/member/<int:member_id>
@member_bp.route("/<int:member_id>")
@jwt_required()
@current_member("server_id")
@member_exist("server_id", "member_id")
def view_one_member(server_id, member_id):
    # Fetch server member from database
    server_member = ServerMember.query.filter_by(server_id=server_id, member_id=member_id).first()
    # Return response
    return server_member_schema.dump(server_member)

# Join as member - POST - route: /server/<int:server_id>/member/join
@member_bp.route("/join", methods=["POST"])
@jwt_required()
def join_server(server_id):
    # Fetch server from database
    server = Server.query.get(server_id)
    # If server does not exist
    if not server:
        # Return response
        return {"error": f"server with id {server_id} not found"}, 404
    # If server exists
    else:
        existing_member = ServerMember.query.filter_by(server=server, user_id=get_jwt_identity()).first(), 201
        # If user is already a member
        if existing_member:
            # Return response if user already a server member
            return {"error": f"user is already a member of server {server.server_name}"}, 400
        # Create instance of ServerMember model
        new_member = ServerMember(
            joined_on = date.today(),
            server = server,
            user_id = get_jwt_identity()
        )
        # Add and commit to database
        db.session.add(new_member)
        db.session.commit()
        # Return response
        return server_member_schema.dump(new_member), 201

# Add member - POST - route: /server/<int:server_id>/member/add/<int:user_id>
@member_bp.route("/add/<int:user_id>", methods=["POST"])
@jwt_required()
@current_member("server_id")
@auth_as_admin("server_id")
def add_member(server_id, user_id):
    # Fetch user from database
    user = User.query.get(user_id)
    # Fetch server from database
    server = Server.query.get(server_id)
    # If user does not exist
    if not user:
        # Return response
        return {"error": f"user with id {user_id} not found"}, 404
    existing_member = ServerMember.query.filter_by(server=server, user_id=user_id).first(), 201
    # If user is already a member
    if existing_member:
        # Return response
        return {"error": f"user {user.username} is already a member of server {server.server_name}"}, 400
    else:
        # Create instance of ServerMember model
        new_member = ServerMember(
            joined_on = date.today(),
            server = server,
            user_id = user_id
        )
        # Add and commit to database
        db.session.add(new_member)
        db.session.commit()
        # Return response
        return server_member_schema.dump(new_member), 201

# Update member - PUT, PATCH - route: /server/<int:server_id>/member/update/<int:member_id>
@member_bp.route("/update/<int:member_id>", methods=["PUT", "PATCH"])
@jwt_required()
@member_exist("server_id", "member_id")
@current_member("server_id")
@auth_as_admin("server_id")
def update_member(server_id, member_id):
    # Get data from body of request
    body_data = request.get_json()
    # Fetch server member from database
    server_member = ServerMember.query.get(member_id)
    # If server member is server creator
    if server_member.user_id == server_member.server.creator_user_id:
        # Return response
        return {"error": f"user {server_member.user.username} cannot be updated or deleted"}, 400
    else:
        # Update server member fields
        server_member.is_admin = body_data.get("is_admin") or server_member.is_admin
        # Commit to database
        db.session.commit()
        # Return response
        return server_member_schema.dump(server_member)

# Delete member - DELETE - route: /server/<int:server_id>/member/delete/<int:member_id>
@member_bp.route("/delete/<int:member_id>", methods=["DELETE"])
@jwt_required()
@member_exist("server_id", "member_id")
@current_member("server_id")
@auth_as_admin("server_id")
def delete_member(server_id, member_id):
    # Fetch server member from database
    server_member = ServerMember.query.filter_by(member_id=member_id).first()
    # If server member is server creator
    if server_member.user_id == server_member.server.creator_user_id:
        # Return response
        return {"error": f"user {server_member.user.username} cannot be updated or deleted"}, 400
    else:
        # Delete and commit to database
        db.session.delete(server_member)
        db.session.commit()
        # Return response
        return {"message": f"member has been deleted from server {server_member.server.server_name}"}