from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from main import db, bcrypt
from models.user import User, UserSchema, user_schema

user_bp = Blueprint("user", __name__, url_prefix="/user")

# Update account - PUT, PATCH - route: /user/updateaccount
@user_bp.route("/updateaccount", methods=["PUT", "PATCH"])
@jwt_required()
def update_account():
    try:
        # Get data from body of request
        body_data = UserSchema().load(request.get_json(), partial=True)
        password = body_data.get("password")
        # Fetch user from database
        user = User.query.get(get_jwt_identity())
        # If user exists, update fields
        if user:
            user.name = body_data.get("name") or user.name
            user.username = body_data.get("username") or user.username
            user.status = body_data.get("status") or user.status
            # If password exists, hash password
            if password:
                user.password = bcrypt.generate_password_hash(password).decode("utf-8")
            # Commit to database
            db.session.commit()
            # Return response
            return user_schema.dump(user)
        else:
            # Return response if user does not exist
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

# Delete account - DELETE - route: /user/deleteaccount
@user_bp.route("/deleteaccount", methods=["DELETE"])
@jwt_required()
def delete_user():
    # Fetch user from database
    user = User.query.get(get_jwt_identity())
    # If user exist, delete and commit to database
    if user:
        db.session.delete(user)
        db.session.commit()
        # Return response
        return {"message": f"user {user.username} has been deleted"}
    else:
        # Return response if user does not exist
        return {"error": "user not found"}, 404