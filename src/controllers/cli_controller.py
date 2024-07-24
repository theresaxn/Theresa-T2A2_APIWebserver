import datetime
from datetime import date

from flask import Blueprint

from main import db, bcrypt
from models.user import User
from models.server import Server
from models.server_member import ServerMember
from models.channel import Channel
from models.friend_request import FriendRequest
from models.message import Message

db_commands = Blueprint("db", __name__)

@db_commands.cli.command("create")
def create_table():
    db.create_all()
    print("Tables created")

@db_commands.cli.command("drop")
def drop_table():
    db.drop_all()
    print("Tables dropped")

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

    server_members = [
        ServerMember(
            joined_on = date.today(),
            is_admin = True,
            server = servers[0],
            user = users[0]
        ),
        ServerMember(
            joined_on = date.today(),
            server = servers[0],
            user = users[1]
        ),
        ServerMember(
            joined_on = date.today(),
            is_admin = True,
            server = servers[1],
            user = users[0]
        ),
        ServerMember(
            joined_on = date.today(),
            is_admin = True,
            server = servers[2],
            user = users[1]
        ),
        ServerMember(
            joined_on = date.today(),
            server = servers[2],
            user = users[0]
        )
    ]

    db.session.add_all(server_members)

    channels = [
        Channel(
            channel_name = "channel 1",
            created_on = date.today(),
            user = users[0],
            server = servers[0]   
        ), 
        Channel(
            channel_name = "channel 2",
            created_on = date.today(),
            user = users[0],
            server = servers[1]   
        ), 
        Channel(
            channel_name = "channel 3",
            created_on = date.today(),
            user = users[1],
            server = servers[2]   
        )
    ]

    db.session.add_all(channels)

    friend_requests = [
        FriendRequest(
            is_accepted = True,
            sender_user = users[0],
            receiver_user = users[1]
        )
    ]

    db.session.add_all(friend_requests)

    messages = [
        Message(
            content = "message 1",
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            sender_user = users[0],
            receiver_user = users[1]
        ),
        Message(
            content = "message 2",
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            channel = channels[0],
            sender_user = users[1]
        )
    ]

    db.session.add_all(messages)

    db.session.commit()
    print("Tables seeded")
