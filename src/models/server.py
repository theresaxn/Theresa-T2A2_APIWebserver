from marshmallow import fields

from main import db, ma

# create servers table in database

class Server(db.Model):
    __tablename__ = "servers"
    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.Date)

    creator_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="servers")

class ServerSchema(ma.Schema):
    user = fields.Nested("UserSchema", only=["id", "username"])

    class Meta:
        fields = ("id", "server_name", "created_at", "creator_user_id")

server_schema = ServerSchema()
servers_schema = ServerSchema(many=True)
