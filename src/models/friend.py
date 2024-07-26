from marshmallow import fields

from main import db, ma

class Friend(db.Model):
    __tablename__ = "friends"
    friend_id = db.Column(db.Integer, primary_key=True)
    is_accepted = db.Column(db.Boolean, default=False)

    user1_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    user1 = db.relationship("User",
                            foreign_keys=[user1_id],
                            back_populates="friend_user1")
    user2_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    user2 = db.relationship("User",
                            foreign_keys=[user2_id],
                            back_populates="friend_user2")
    

class FriendSchema(ma.Schema):
    user1 = fields.Nested("UserSchema", only=["user_id", "username", "name", "status"])
    user2 = fields.Nested("UserSchema", only=["user_id", "username", "name", "status"])

    class Meta:
        fields = ("id", "is_accepted", "user1", "user2")

friend_schema = FriendSchema()
friends_schema = FriendSchema(many=True)

