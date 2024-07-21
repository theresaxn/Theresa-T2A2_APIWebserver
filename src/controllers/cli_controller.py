from datetime import date

from flask import Blueprint

from main import db, bcrypt
from models.user import User
from models.server import Server

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
            name = "user 1",
            status = "online"
        ),
        User(
            username = "user2",
            email = "user2@email.com",
            password = bcrypt.generate_password_hash("123456").decode("utf-8"),
            name = "user 2",
            status = "offline"
        )
    ]

    db.session.add_all(users)

    servers = [
        Server(
            server_name = "server 1",
            created_on = date.today(),
            user = users[0]
        ),
        Server(
            server_name = "server 2",
            created_on = date.today(),
            user = users[0]
        ),
        Server(
            server_name = "server a",
            created_on = date.today(),
            user = users[1]
        )
    ]

    db.session.add_all(servers)

    db.session.commit()
    print("tables seeded")
