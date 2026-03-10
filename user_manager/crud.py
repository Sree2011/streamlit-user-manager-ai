from .models import User, session
from .utils import validate_input

def add_user(name: str, role: str):
    if not validate_input(name, role):
        return "Invalid input"
    new_user = User(name=name, role=role)
    session.add(new_user)
    session.commit()
    return new_user

def list_users():
    return session.query(User).all()

def update_user(user_id: int, name: str = "", role: str = ""):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return None
    if name:
        user.name = name   # ✅ assign to instance, not Column
    if role:
        user.role = role
    session.commit()
    return user

def delete_user(user_id: int):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return None
    session.delete(user)
    session.commit()
    return True