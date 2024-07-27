from marshmallow import fields
from marshmallow.validate import Length

from main import db, ma

# Create Server model in database
class Server(db.Model):

    # Define table name
    __tablename__ = "servers"

    # Define column name and attributes
    server_id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String, nullable=False)
    created_on = db.Column(db.Date)

    # Define foreign keys and relationships
    creator_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    user = db.relationship("User", back_populates="servers")

    server_members = db.relationship("ServerMember", back_populates="server", cascade="all, delete")
    channels = db.relationship("Channel", back_populates="server", cascade="all, delete")

# Schema for Server model
class ServerSchema(ma.Schema):

    # Define nested fields
    user = fields.Nested("UserSchema", only=["user_id", "username"])
    server_members = fields.List(fields.Nested("ServerMemberSchema", exclude=["server"]))
    channels = fields.List(fields.Nested("ChannelSchema", exclude=["server", "user", "messages"]))

    # Define field validations
    server_name = fields.String(validate=Length(min=5, error="must be at least 5 characters long"))

    class Meta:
        fields = ("server_id", "server_name", "created_on", "user", "server_members", "channels")

# To handle single server object
server_schema = ServerSchema()

# To handle list of server objects
servers_schema = ServerSchema(many=True)
