from marshmallow import fields, ValidationError
from marshmallow.validate import Regexp

from main import db, ma
    
# Create User model in database
class User(db.Model):

    # Define table name
    __tablename__ = "users"

    # Define column name and attributes
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    status = db.Column(db.String, default="offline")

    # Define foreign key relationships
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

# Schema for User model
class UserSchema(ma.Schema):

    # Define nested fields
    servers = fields.List(fields.Nested("ServerSchema", exclude=["user"]))
    server_members = fields.List(fields.Nested("ServerMemberSchema", exclude=["user"]))
    channels = fields.List(fields.Nested("ChannelSchema", exclude=["user"]))
    messages_sender = fields.List(fields.Nested("MessageSchema", exclude=["sender_user"]))
    messages_receiver = fields.List(fields.Nested("MessageSchema", exclude=["receiver_user"]))

    # Define field validations
    password = fields.String(validate=Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
                                             error= "needs to be minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character"))
    status = fields.String(validate=validate_status)

    class Meta:
        fields = ("user_id", "username", "email", "password", "name", "status", "servers", "server_members",
                  "channels", "messages_sender", "messages_receiver")

# To handle single user object
user_schema = UserSchema(only=["user_id", "username", "email", "name", "status", "servers"])

# To handle list of user objects
users_schema = UserSchema(exclude=["user_id", "username", "email", "name", "status", "servers"], many=True)