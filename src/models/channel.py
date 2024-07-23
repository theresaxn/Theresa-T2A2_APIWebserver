from marshmallow import fields

from main import db, ma

class Channel(db.Model):
    __tablename__ = "channels"
    id = db.Column(db.Integer, primary_key=True)
    channel_name = db.Column(db.String, nullable=False)
    created_on = db.Column(db.Date)

    creator_user_id = db.Column(db.Integer, db.ForeignKey("users.id", nullable=False))
    user = db.relationship("User", back_populates ="channels")

    server_id = db.Column(db.Integer, db.ForeignKey("servers.id", nullable=False))
    server = db.relationship("Server", back_populates="channels")

class ChannelSchema(ma.Schema):
    user = fields.Nested("UserSchema", only=["id", "username", "name", "status"])
    server = fields.Nested("ServerSchema", exclude=["channels"])

    class Meta:
        fields = ("id", "channel_name", "created_on", "user", "server")

channel_schema = ChannelSchema()
channels_schema = ChannelSchema(many=True)