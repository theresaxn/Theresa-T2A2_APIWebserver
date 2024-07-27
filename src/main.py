import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from marshmallow.exceptions import ValidationError

db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
jwt = JWTManager()

# create, configure and initialise flask app
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    @app.errorhandler(ValidationError)
    def validation_error(err):
        return {"error": err.messages}, 400

    from controllers.cli_controller import db_commands
    app.register_blueprint(db_commands)

    from controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)

    from controllers.user_controller import user_bp
    app.register_blueprint(user_bp)
    
    from controllers.server_controller import server_bp
    app.register_blueprint(server_bp)
    
    from controllers.server_member_controller import member_bp
    app.register_blueprint(member_bp)

    return app