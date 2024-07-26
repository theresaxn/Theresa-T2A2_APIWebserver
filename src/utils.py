from flask_jwt_extended import get_jwt_identity

from main import db
from models.server import Server
from models.server_member import ServerMember

# Check if user is an existing member in a server
def existing_member(server_id):
    server_stmt = db.select(Server).filter_by(server_id=server_id)
    server = db.session.scalar(server_stmt)
    member_stmt = db.select(ServerMember).filter_by(server=server, user_id=get_jwt_identity())
    server_member = db.session.scalar(member_stmt)
    return server_member

