from marshmallow import fields

from main import db, ma

class Channel(db.Model):
    __tablename__ = "channels"
    channel_id = db.Column(db.Integer, primary_key=True)
    channel_name = db.Column(db.String, nullable=False)
    created_on = db.Column(db.Date)

    creator_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    user = db.relationship("User", back_populates ="channels")

    server_id = db.Column(db.Integer, db.ForeignKey("servers.server_id"), nullable=False)
    server = db.relationship("Server", back_populates="channels")

    messages = db.relationship("Message", back_populates="channel", cascade="all, delete")

class ChannelSchema(ma.Schema):
    user = fields.Nested("UserSchema", only=["user_id", "username"])
    server = fields.Nested("ServerSchema", exclude=["channels"])
    messages = fields.List(fields.Nested("MessageSchema", exclude=["channel"]))

    class Meta:
        fields = ("channel_id", "channel_name", "created_on", "user", "server", "messages")

channel_schema = ChannelSchema()
channels_schema = ChannelSchema(many=True)