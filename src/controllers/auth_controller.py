from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from main import db, bcrypt
from models.user import User, UserSchema, user_schema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Register new user - POST method - route: /auth/register
@auth_bp.route("/register", methods=["POST"])
def register_user():
    try:
        # Get data from body of request
        body_data = UserSchema().load(request.get_json())
        # Create instance of User model
        user = User(
            username = body_data.get("username"),
            email = body_data.get("email"),
            name = body_data.get("name"),
            status = body_data.get("status")
        )
        # Get password from body of request
        password = body_data.get("password")
        # If password exists, hash password
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        # Add and commit to database
        db.session.add(user)
        db.session.commit()
        # Return response
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

# Login user - POST method - route: /auth/login
@auth_bp.route("/login", methods=["POST"])
def login_user():
    # Get data from body of request
    body_data = request.get_json()
    # Fetch user in database
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    # Check if user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # Create JWT token
        token = create_access_token(identity=str(user.user_id), expires_delta=timedelta(days=1))
        # Return response
        return {"message": f"welcome back {user.username}", "token": token}
    else:
        # Return response if error
        return {"error": "invalid login details"}, 409