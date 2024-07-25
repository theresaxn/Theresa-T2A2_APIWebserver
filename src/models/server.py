from marshmallow import fields
from marshmallow.validate import Length

from main import db, ma

# create servers table in database
class Server(db.Model):
    __tablename__ = "servers"
    server_id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String, nullable=False)
    created_on = db.Column(db.Date)

    creator_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    user = db.relationship("User", back_populates="servers")

    server_members = db.relationship("ServerMember", back_populates="server", cascade="all, delete")
    channels = db.relationship("Channel", back_populates="server", cascade="all, delete")

class ServerSchema(ma.Schema):
    user = fields.Nested("UserSchema", only=["user_id", "username"])
    server_members = fields.List(fields.Nested("ServerMemberSchema", only=["member_id", "user"]))
    channels = fields.List(fields.Nested("ChannelSchema", only=["channel_id", "channel_name"]))

    server_name = fields.String(validate=Length(min=5, error="must be at least 5 characters long"))

    class Meta:
        fields = ("server_id", "server_name", "created_on", "user", "server_members", "channels")
        ordered = True

server_schema = ServerSchema()
servers_schema = ServerSchema(many=True)
