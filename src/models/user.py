from marshmallow import fields

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
    friends_sender = db.relationship("FriendRequest",
                                     foreign_keys="[FriendRequest.sender_user_id]",
                                     back_populates="sender_user",
                                     cascade="all, delete")
    friends_receiver = db.relationship("FriendRequest",
                                       foreign_keys="[FriendRequest.receiver_user_id]",
                                       back_populates="receiver_user",
                                       cascade="all, delete")
    messages_sender = db.relationship("Message",
                                      foreign_keys="[Message.sender_user_id]",
                                      back_populates="sender_user",
                                      cascade="all, delete")
    messages_receiver = db.relationship("Message",
                                        foreign_keys="[Message.receiver_user_id]",
                                        back_populates="receiver_user",
                                        cascade="all, delete")

class UserSchema(ma.Schema):
    servers = fields.List(fields.Nested("ServerSchema", exclude=["user"]))
    server_members = fields.List(fields.Nested("ServerMemberSchema", exclude=["user"]))
    channels = fields.List(fields.Nested("ChannelSchema", exclude=["user"]))
    friends_sender = fields.List(fields.Nested("FriendRequestSchema", exclude=["sender_user"]))
    friends_receiver = fields.List(fields.Nested("FriendRequestSchema", exclude=["receiver_user"]))
    messages_sender = fields.List(fields.Nested("MessageSchema", exclude=["sender_user"]))
    messages_receiver = fields.List(fields.Nested("MessageSchema", exclude=["receiver_user"]))

    class Meta:
        fields = ("user_id", "username", "email", "password", "name", "status", "servers", "server_members",
                  "channels", "friends_sender", "friends_receiver", "messages_sender", "messages_receiver")

user_schema = UserSchema(exclude=["password"])
users_schema = UserSchema(exclude=["password"], many=True)
