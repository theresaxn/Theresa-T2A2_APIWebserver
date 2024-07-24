from marshmallow import fields

from main import db, ma

class FriendRequest(db.Model):
    __tablename__ = "friend_requests"
    friend_id = db.Column(db.Integer, primary_key=True)
    is_accepted = db.Column(db.Boolean, default=False)
    
    sender_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    sender_user = db.relationship("User", foreign_keys=[sender_user_id],
                                  back_populates="friends_sender")

    receiver_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    receiver_user = db.relationship("User", foreign_keys=[receiver_user_id],
                                    back_populates="friends_receiver")

class FriendRequestSchema(ma.Schema):
    sender_user = fields.Nested("UserSchema", only=["user_id", "username"])
    reciever_user = fields.Nested("UserSchema", only=["user_id", "username"])

    class Meta:
        fields = ("friend_id", "is_accepted", "sender_user", "receiver_user")

friend_request_schema = FriendRequestSchema()
friend_requests_schema = FriendRequestSchema(many=True)