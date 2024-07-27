from marshmallow import fields

from main import db, ma

# create servers table in database
class ServerMember(db.Model):
    __tablename__ = "server_members"
    member_id = db.Column(db.Integer, primary_key=True)
    joined_on = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    
    server_id = db.Column(db.Integer, db.ForeignKey("servers.server_id"), nullable=False)
    server = db.relationship("Server", back_populates="server_members")

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    user = db.relationship("User", back_populates="server_members")

class ServerMemberSchema(ma.Schema):
    server = fields.Nested("ServerSchema", only=["server_id", "server_name"])
    user = fields.Nested("UserSchema", only=["user_id", "username"])

    class Meta:
        fields = ("member_id", "joined_on", "is_admin", "server", "user")

server_member_schema = ServerMemberSchema()
server_members_schema = ServerMemberSchema(many=True)