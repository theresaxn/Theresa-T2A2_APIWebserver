import functools

from flask_jwt_extended import get_jwt_identity

from main import db
from models.user import User
from models.server import Server
from models.server_member import ServerMember
from models.channel import Channel
from models.message import Message

def current_member(id_arg_name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs): 
            server_id = kwargs.get(id_arg_name)
            server = Server.query.get(server_id)
            if not server:
                return {"error": f"server with id {server_id} not found"}, 404
            server_member = ServerMember.query.filter_by(server=server, user_id=get_jwt_identity()).first()
            if not server_member:
                return {"error": f"user not a member of server {server.server_name}"}, 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def auth_as_admin (id_arg_name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs): 
            server_id = kwargs.get(id_arg_name)
            server = Server.query.get(server_id)
            server_member = ServerMember.query.filter_by(server=server, user_id=get_jwt_identity()).first()
            if not server_member.is_admin:
                return {"error": "user not authorised to perform this action"}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def member_exist(id1_arg_name, id2_arg_name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs): 
            server_id = kwargs.get(id1_arg_name)
            member_id = kwargs.get(id2_arg_name)
            server = Server.query.get(server_id)
            server_member = ServerMember.query.get(member_id)
            if not server:
                return {"error": f"server with id {server_id} not found"}, 404
            if not server_member:
                return {"error": f"member with id {member_id} not found"}, 404
            member_filter = ServerMember.query.filter_by(server=server, member_id=member_id).first()
            if not member_filter:
                return {"error": f"member with id {member_id} not found in server {server.server_name}"}, 404
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def channel_exist(id1_arg_name, id2_arg_name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs): 
            server_id = kwargs.get(id1_arg_name)
            channel_id = kwargs.get(id2_arg_name)
            server = Server.query.get(server_id)
            channel = Channel.query.get(channel_id)
            if not server:
                return {"error": f"server with id {server_id} not found"}, 404
            if not channel:
                return {"error": f"channel with id {channel_id} not found"}, 404
            channel_filter = Channel.query.filter_by(server=server, channel_id=channel_id).first()
            if not channel_filter:
                return {"error": f"channel with id {channel_id} not found in server {server.server_name}"}, 404
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def channel_message_exist(id1_arg_name, id2_arg_name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs): 
            channel_id = kwargs.get(id1_arg_name)
            message_id = kwargs.get(id2_arg_name)
            channel = Channel.query.get(channel_id)
            message = Message.query.get(message_id)
            if not channel:
                return {"error": f"channel with id {channel_id} not found"}, 404
            if not message:
                return {"error": f"message with id {message_id} not found"}, 404
            message_filter = Message.query.filter_by(channel=channel, message_id=message_id).first()
            if not message_filter:
                return {"error": f"message with id {message_id} not found in channel {channel.channel_name}"}, 404
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def message_exist(id1_arg_name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs): 
            message_id = kwargs.get(id1_arg_name)
            message = Message.query.get(message_id)
            if not message:
                return {"error": f"message with id {message_id} not found"}, 404
            message_filter = Message.query.filter_by(message_id=message_id, sender_user_id=get_jwt_identity()).first()
            if not message_filter:
                return {"error": f"message with id {message_id} does not belong to user"}, 404
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def current_member_check(id_arg_name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs): 
            channel_id = kwargs.get(id_arg_name)
            channel = Channel.query.get(channel_id)
            if not channel:
                return {"error": f"channel with id {channel_id} not found"}, 404
            server = Server.query.get(channel.server.server_id)
            server_member = ServerMember.query.filter_by(server=server, user_id=get_jwt_identity()).first()
            if not server_member:
                return {"error": f"user not a member of server {server.server_name}"}, 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator