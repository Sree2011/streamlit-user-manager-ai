# utils.py

def validate_input(name: str, role: str) -> bool:
    return bool(name and role)

def format_user(user) -> dict:
    if not user:
        return {}
    return {"id": user.id, "name": user.name, "role": user.role}