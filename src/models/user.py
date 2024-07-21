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

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "email", "password", "name", "status")

user_schema = UserSchema(exclude=["password"])
users_schema = UserSchema(exclude=["password"], many=True)
