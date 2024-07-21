from flask import Blueprint

from main import db, bcrypt
from models.user import User

db_commands = Blueprint("db", __name__)

@db_commands.cli.command("create")
def create_table():
    db.create_all()
    print("tables created")

@db_commands.cli.command("drop")
def drop_table():
    db.drop_all()
    print("tables dropped")

@db_commands.cli.command("seed")
def seed_table():
    users = [
        User(
            username = "user1",
            email = "user1@email.com",
            password = bcrypt.generate_password_hash("123456").decode("utf-8"),
            name = "User 1",
            status = "online"
        ),
        User(
            username = "user2",
            email = "user2@email.com",
            password = bcrypt.generate_password_hash("123456").decode("utf-8"),
            name = "User 2",
            status = "offline"
        )
    ]
    db.session.add_all(users)
    db.session.commit()
    print("tables seeded")
