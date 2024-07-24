from marshmallow import fields

from main import db, ma

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.Date)
    
    channel_id = db.Column(db.Integer, db.ForeignKey("channels.id"), nullable=True)
    channel = db.relationship("Channel", back_populates="messages")

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="messages")

class MessageSchema(ma.Schema):
    channel = fields.Nested("ChannelSchema", exclude=["messages"])
    user = fields.Nested("UserSchema", only=["id", "username", "name", "status"])
    
    class Meta:
        fields = ("id", "content", "timestamp", "channel", "user")

message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)