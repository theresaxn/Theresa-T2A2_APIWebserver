from marshmallow import fields

from main import db, ma

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.Date)
    
    channel_id = db.Column(db.Integer, db.ForeignKey("channels.id"), nullable=True)
    channel = db.relationship("Channel", back_populates="messages")

    sender_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    sender_user = db.relationship("User",foreign_keys=[sender_user_id],
                                  back_populates="messages_sender")

    receiver_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    receiver_user = db.relationship("User", foreign_keys=[receiver_user_id],
                                    back_populates="messages_receiver")

class MessageSchema(ma.Schema):
    channel = fields.Nested("ChannelSchema", exclude=["messages"])
    sender_user = fields.Nested("UserSchema", only=["id", "username", "name", "status"])
    receiver_user = fields.Nested("UserSchema", only=["id", "username", "name", "status"])
    
    class Meta:
        fields = ("id", "content", "timestamp", "channel", "sender_user", "receiver_user")

message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)