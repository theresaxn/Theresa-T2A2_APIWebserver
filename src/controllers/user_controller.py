from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from main import db
from models.user import User, UserSchema, user_schema, users_schema

user_bp = Blueprint("user", __name__, url_prefix="/user")

# Update account - PUT, PATCH - user/updateaccount
@user_bp.route("/updateaccount", methods=["PUT", "PATCH"])
@jwt_required()
def update_account():
    body_data = UserSchema().load(request.get_json(), partial=True)
    password = body_data.get("password")
    stmt = db.select(User).filter_by(user_id=get_jwt_identity())
    user = db.session.scalar(stmt)
    if user:
        user.name = body_data.get("name") or user.name
        user.username = body_data.get("username") or user.username
        user.status = body_data.get("status") or user.status
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        db.session.commit()
        return user_schema.dump(user)
    else:
        return {"error": "user not found"}, 404

# Delete account - DELETE - user/deleteaccount
@user_bp.route("/deleteaccount", methods=["DELETE"])
@jwt_required()
def delete_user():
    stmt = db.select(User).filter_by(user_id=get_jwt_identity())
    user = db.session.scalar(stmt)
    if user:
        db.session.delete(user)
        db.session.commit()
        return {"message": f"user {user.username} has been deleted"}
    else:
        return {"error": "user not found"}, 404