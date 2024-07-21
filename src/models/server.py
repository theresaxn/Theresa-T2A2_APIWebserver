from marshmallow import fields

from main import db, ma

# create servers table in database
class Server(db.Model):
    __tablename__ = "servers"
    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String, nullable=False)
    created_on = db.Column(db.Date)

    creator_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="servers")

    server_members = db.relationship("ServerMember", back_populates="server", cascade="all, delete")

class ServerSchema(ma.Schema):
    user = fields.Nested("UserSchema", only=["id", "username"])
    server_members = fields.List(fields.Nested("ServerMemberSchema", exclude=["user"]))

    class Meta:
        fields = ("id", "server_name", "created_on", "user", "server_members")

server_schema = ServerSchema()
servers_schema = ServerSchema(many=True)
