from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from main import db, bcrypt
from models.user import User, UserSchema, user_schema, users_schema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Register - POST - auth/register
@auth_bp.route("/register", methods=["POST"])
def register_user():
    try:
        body_data = UserSchema().load(request.get_json())
        user = User(
            username = body_data.get("username"),
            email = body_data.get("email"),
            name = body_data.get("name"),
            status = body_data.get("status")
        )
        password = body_data.get("password")
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is required"}, 409
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            constraint_detail = err.orig.diag.constraint_name
            if "users_username_key" in constraint_detail:
                column_name = "username"
            elif "users_email_key" in constraint_detail:
                column_name = "email"
            else:
                column_name = "unknown"
            return {"error": f"{column_name} already in use"}, 409

# Login - POST - auth/login
@auth_bp.route("/login", methods=["POST"])
def login_user():
    body_data = request.get_json()
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        token = create_access_token(identity=str(user.user_id), expires_delta=timedelta(days=1))
        return {"message": f"welcome back {user.username}", "token": token}
    else:
        return {"error": "invalid login details"}, 409