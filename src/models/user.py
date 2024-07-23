from marshmallow import fields

from main import db, ma

# create users table in database
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    status = db.Column(db.String, default="offline")

    servers = db.relationship("Server", back_populates="user", cascade="all, delete")
    server_members = db.relationship("ServerMember", back_populates="user", cascade="all, delete")
    channels = db.relationship("Channel", back_populates="user", cascade="all,delete")

class UserSchema(ma.Schema):
    servers = fields.List(fields.Nested("ServerSchema", exclude=["user"]))
    server_members = fields.List(fields.Nested("ServerMemberSchema", exclude=["user"]))
    channels = fields.List(fields.Nested("ChannelSchema", exclude=["user"]))
    
    class Meta:
        fields = ("id", "username", "email", "password", "name", "status", "servers", "server_members", "channels")

user_schema = UserSchema(exclude=["password"])
users_schema = UserSchema(exclude=["password"], many=True)
