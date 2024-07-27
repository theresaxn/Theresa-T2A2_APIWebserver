from marshmallow import fields
from marshmallow.validate import Length

from main import db, ma

# Create Message model in database
class Message(db.Model):

    # Define table name
    __tablename__ = "messages"

    # Define column name and attributes
    message_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime)
    
    # Define foreign keys and relationships
    channel_id = db.Column(db.Integer, db.ForeignKey("channels.channel_id"), nullable=True)
    channel = db.relationship("Channel", back_populates="messages")

    sender_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    sender_user = db.relationship("User",
                                  foreign_keys=[sender_user_id],
                                  back_populates="messages_sender")

    receiver_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True)
    receiver_user = db.relationship("User",
                                    foreign_keys=[receiver_user_id],
                                    back_populates="messages_receiver")

# Schema for Message model
class MessageSchema(ma.Schema):

    # Define nested fields
    channel = fields.Nested("ChannelSchema", only=["channel_id", "channel_name"])
    sender_user = fields.Nested("UserSchema", only=["user_id", "name", "status"])
    receiver_user = fields.Nested("UserSchema", only=["user_id", "name", "status"])
    
    class Meta:
        fields = ("message_id", "title", "content", "timestamp", "channel", "sender_user", "receiver_user")

# To handle single message object
message_schema = MessageSchema()

# To handle list of message objects
messages_schema = MessageSchema(many=True)