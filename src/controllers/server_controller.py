from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from main import db
from models.user import User
from models.server import Server, server_schema, servers_schema
from models.server_member import ServerMember
from controllers.server_member_controller import member_bp
from controllers.channel_controller import channel_bp

server_bp = Blueprint("server", __name__, url_prefix="/server")
server_bp.register_blueprint(member_bp)
server_bp.register_blueprint(channel_bp)

# View all servers - GET - route: /server/all/user/<int:user_id>
@server_bp.route("/all/user/<int:user_id>")
@jwt_required()
def view_all_servers(user_id):
    # Fetch user from database
    user = User.query.get(user_id)
    # If user does not exist
    if not user:
        # Return response
        return {"error": f"user with id {user_id} not found"}, 404
    # Fetch servers from database
    servers = Server.query.filter_by(creator_user_id=user_id).all()
    # If no servers exist
    if not servers:
        # Return response
        return {"message": f"no servers created by {user.username}"}, 200
    else:
        # Return response if servers exist
        return servers_schema.dump(servers)

# View one server - GET - route: /server/<int:server_id>
@server_bp.route("/<int:server_id>")
@jwt_required()
def view_one_server(server_id):
    # Fetch server from database
    server = Server.query.get(server_id)
    # If server does not exist
    if not server:
        # Return response
        return {"error": f"server with id {server_id} not found"}, 404
    return server_schema.dump(server)

# Add server - POST - route: /server/create
@server_bp.route("/create", methods=["POST"])
@jwt_required()
def create_server():
    try: 
        # Get data from body of request
        body_data = server_schema.load(request.get_json())
        # Create instance of Server model
        new_server = Server(
            server_name = body_data.get("server_name"),
            created_on = date.today(),
            creator_user_id = get_jwt_identity()
        )
        # Add and commit to database
        db.session.add(new_server)
        db.session.commit()

        # Create instance of ServerMember model
        new_member = ServerMember(
            joined_on = date.today(),
            server_id = new_server.server_id,
            user_id = get_jwt_identity(),
            is_admin = True
        )
        # Add and commit to database
        db.session.add(new_member)
        db.session.commit()
        # Return response
        return server_schema.dump(new_server), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is required"}, 409
        
# Update server - PATCH, PUT - route: /server/update/<int:server_id>
@server_bp.route("/update/<int:server_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_server(server_id):
    # Get data from body of request
    body_data = server_schema.load(request.get_json())
    # Fetch server from database
    server = Server.query.get(server_id)
    # If server does not exist
    if not server:
        # Return response
        return {"error": f"server with id {server_id} not found"}, 404
    # If server exists
    else:
        # If server creator user is not the same as user
        if str(server.creator_user_id) != get_jwt_identity():
            # Return response
            return {"error": "user not authorised to perform this action"}, 403
        # Update server fields
        server.server_name = body_data.get("server_name") or server.server_name
        # Commit to database
        db.session.commit()
        # Return response
        return server_schema.dump(server)

# Delete server - DELETE - route: /server/delete/<int:server_id>
@server_bp.route("/delete/<int:server_id>", methods=["DELETE"])
@jwt_required()
def delete_server(server_id):
    # Fetch server from database
    server = Server.query.get(server_id)
    # If server does not exist
    if not server:
        return {"error": f"server with id {server_id} not found"}, 404
    # If server exists
    else:
        # If server creator user is not the same as user
        if str(server.creator_user_id) != get_jwt_identity():
            # Return response
            return {"error": "user not authorised to perform action"}, 403
        # Delete and commit to database
        db.session.delete(server)
        db.session.commit()
        # Return response
        return {"message": f"server {server.server_name} has been deleted"}