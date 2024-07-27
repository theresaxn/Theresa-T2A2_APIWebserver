import functools

from flask_jwt_extended import get_jwt_identity

from main import db
from models.user import User
from models.server import Server
from models.server_member import ServerMember

def auth_member_action(id_arg_name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs): 
            member_id = kwargs.get(id_arg_name)
            member = ServerMember.query.get(member_id)
            if not member:
                return {"error": f"member with id {member_id} not found"}, 404
            server = Server.query.get(member.server_id)
            stmt = db.select(ServerMember).filter_by(server=server, user_id=get_jwt_identity())
            server_member = db.session.scalar(stmt)
            if not server_member:
                return {"error": f"user not a member of server {server.server_name}"}, 404
            if not server_member.is_admin:
                return {"error": "user not authorised to perform this action"}, 403
            if member.user.user_id == server.user.user_id:
                return {"error": f"member {server_member.user.username} cannot be updated or deleted"}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator