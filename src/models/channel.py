from marshmallow import fields
from marshmallow.validate import Length

from main import db, ma

# Create Channel model in database
class Channel(db.Model):

    # Define table name
    __tablename__ = "channels"

    # Define column name and attributes
    channel_id = db.Column(db.Integer, primary_key=True)
    channel_name = db.Column(db.String, nullable=False)
    created_on = db.Column(db.Date)

    # Define foreign keys and relationships
    creator_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    user = db.relationship("User", back_populates ="channels")

    server_id = db.Column(db.Integer, db.ForeignKey("servers.server_id"), nullable=False)
    server = db.relationship("Server", back_populates="channels")

    messages = db.relationship("Message", back_populates="channel", cascade="all, delete")

# Schema for Channel model
class ChannelSchema(ma.Schema):

    # Define nested fields
    user = fields.Nested("UserSchema", only=["user_id", "username"])
    server = fields.Nested("ServerSchema", only=["server_id", "server_name"])
    messages = fields.List(fields.Nested("MessageSchema", only=["message_id", "content", "timestamp", "sender_user"]))

    # Define field validations
    channel_name = fields.String(validate=Length(min=5, error="must be at least 5 characters long"))

    class Meta:
        fields = ("channel_id", "channel_name", "created_on", "user", "server", "messages")

# To handle single channel object
channel_schema = ChannelSchema()

# To handle list of channel objects
channels_schema = ChannelSchema(many=True)