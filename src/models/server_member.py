from marshmallow import fields

from main import db, ma

# Create ServerMember model in database
class ServerMember(db.Model):
    
    # Define table name
    __tablename__ = "server_members"

    # Define column name and attributes
    member_id = db.Column(db.Integer, primary_key=True)
    joined_on = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Define foreign keys and relationships
    server_id = db.Column(db.Integer, db.ForeignKey("servers.server_id"), nullable=False)
    server = db.relationship("Server", back_populates="server_members")

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    user = db.relationship("User", back_populates="server_members")

# Schema for ServerMember model
class ServerMemberSchema(ma.Schema):

    # Define nested fields
    server = fields.Nested("ServerSchema", only=["server_id", "server_name"])
    user = fields.Nested("UserSchema", only=["user_id", "username"])

    class Meta:
        fields = ("member_id", "joined_on", "is_admin", "server", "user")

# To handle single server member object
server_member_schema = ServerMemberSchema()

# To handle list of server member objects
server_members_schema = ServerMemberSchema(many=True)