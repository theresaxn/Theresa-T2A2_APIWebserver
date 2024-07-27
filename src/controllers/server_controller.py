from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from main import db
from models.user import User
from models.server import Server, server_schema, servers_schema
from models.server_member import ServerMember
from controllers.server_member_controller import member_bp

server_bp = Blueprint("server", __name__, url_prefix="/server")
server_bp.register_blueprint(member_bp)

# View all servers - GET - server/all/user/<int:user_id>
@server_bp.route("/all/user/<int:user_id>")
@jwt_required()
def view_all_servers(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": f"user with id {user_id} not found"}, 404
    servers = Server.query.filter_by(creator_user_id=user_id).all()
    if not servers:
        return {"error": f"servers created by user {user.username} not found"}, 404
    else:
        return servers_schema.dump(servers)

# View one server - GET - server/<int:server_id>
@server_bp.route("/<int:server_id>")
@jwt_required()
def view_one_server(server_id):
    server = Server.query.get(server_id)
    if not server:
        return {"error": f"server with id {server_id} not found"}, 404
    return server_schema.dump(server)

# Add server - POST - server/create
@server_bp.route("/create", methods=["POST"])
@jwt_required()
def create_server():
    body_data = server_schema.load(request.get_json())
    new_server = Server(
        server_name = body_data.get("server_name"),
        created_on = date.today(),
        creator_user_id = get_jwt_identity()
    )
    db.session.add(new_server)
    db.session.commit()

    new_member = ServerMember(
        joined_on = date.today(),
        server_id = new_server.server_id,
        user_id = get_jwt_identity(),
        is_admin = True
    )

    db.session.add(new_member)
    db.session.commit()
    return server_schema.dump(new_server)

# Update server - PATCH, PUT - server/update/<int:server_id>
@server_bp.route("/update/<int:server_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_server(server_id):
    body_data = server_schema.load(request.get_json())
    stmt = db.select(Server).filter_by(server_id=server_id)
    server = db.session.scalar(stmt)
    if not server:
        return {"error": f"server with id {server_id} not found"}, 404
    else:
        if str(server.creator_user_id) != get_jwt_identity():
            return {"error": "user not authorised to perform this action"}, 403
        server.server_name = body_data.get("server_name") or server.server_name
        db.session.commit()
        return server_schema.dump(server)

# Delete server - DELETE - server/delete/<int:server_id>
@server_bp.route("/delete/<int:server_id>", methods=["DELETE"])
@jwt_required()
def delete_server(server_id):
    stmt = db.select(Server).filter_by(server_id=server_id)
    server = db.session.scalar(stmt)
    if not server:
        return {"error": f"server with id {server_id} not found"}, 404
    else:
        if str(server.creator_user_id) != get_jwt_identity():
            return {"error": "user not authorised to perform action"}, 403
        db.session.delete(server)
        db.session.commit()
        return {"message": f"server {server.server_name} has been deleted"}