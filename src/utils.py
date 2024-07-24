import functools

from flask_jwt_extended import get_jwt_identity

from main import db
from models.user import User

def auth_as_admin(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        stmt = db.select(User).filter_by(id=user_id)
        user = db.session.scalar(stmt)
        if user.is_admin:
            return fn(*args, **kwargs)
        else:
            return {"error": "user is not authorised to perform this action"}, 403
    return wrapper