from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from main import db
from models.user import User, UserSchema, user_schema

user_bp = Blueprint("user", __name__, url_prefix="/user")

# Update account - PUT, PATCH - user/updateaccount
@user_bp.route("/updateaccount", methods=["PUT", "PATCH"])
@jwt_required()
def update_account():
    try:
        body_data = UserSchema().load(request.get_json(), partial=True)
        password = body_data.get("password")
        user = User.query.get(get_jwt_identity())
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
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is required"}, 409
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            constraint_detail = err.orig.diag.constraint_name
            if "users_username_key" in constraint_detail:
                column_name = "username"
            else:
                column_name = "unknown"
            return {"error": f"{column_name} already in use"}, 409

# Delete account - DELETE - user/deleteaccount
@user_bp.route("/deleteaccount", methods=["DELETE"])
@jwt_required()
def delete_user():
    user = User.query.get(get_jwt_identity())
    if user:
        db.session.delete(user)
        db.session.commit()
        return {"message": f"user {user.username} has been deleted"}
    else:
        return {"error": "user not found"}, 404