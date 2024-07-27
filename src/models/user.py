from marshmallow import fields, ValidationError
from marshmallow.validate import Regexp

from main import db, ma
    
# create users table in database
class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    status = db.Column(db.String, default="offline")

    servers = db.relationship("Server", back_populates="user", cascade="all, delete")
    server_members = db.relationship("ServerMember", back_populates="user", cascade="all, delete")
    channels = db.relationship("Channel", back_populates="user", cascade="all, delete")
    
    messages_sender = db.relationship("Message",
                                      foreign_keys="[Message.sender_user_id]",
                                      back_populates="sender_user",
                                      cascade="all, delete")
    messages_receiver = db.relationship("Message",
                                        foreign_keys="[Message.receiver_user_id]",
                                        back_populates="receiver_user",
                                        cascade="all, delete")

VALID_STATUSES = ("online", "offline", "away")

def validate_status(status):
    if status.lower() not in VALID_STATUSES:
        raise ValidationError(f"must be one of: online, offline, away")

class UserSchema(ma.Schema):
    servers = fields.List(fields.Nested("ServerSchema", exclude=["user"]))
    server_members = fields.List(fields.Nested("ServerMemberSchema", exclude=["user"]))
    channels = fields.List(fields.Nested("ChannelSchema", exclude=["user"]))
    messages_sender = fields.List(fields.Nested("MessageSchema", exclude=["sender_user"]))
    messages_receiver = fields.List(fields.Nested("MessageSchema", exclude=["receiver_user"]))

    password = fields.String(validate=Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
                                             error= "needs to be minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character"))
    status = fields.String(validate=validate_status)

    class Meta:
        fields = ("user_id", "username", "email", "password", "name", "status", "servers", "server_members",
                  "channels", "messages_sender", "messages_receiver")

user_schema = UserSchema(only=["user_id", "username", "email", "name", "status", "servers"])
users_schema = UserSchema(exclude=["user_id", "username", "email", "name", "status", "servers"], many=True)