from typing import Optional
import mongoengine
from src.account.user import User


active_account: Optional[User] = None


def reload_account():
    global active_account
    if not active_account:
        return
    active_account = find_account_by_email(active_account.email)


def create_account(name: str, email: str) -> User:
    user = User()
    user.name = name
    user.email = email
    user.save()
    return user




def find_account_by_email(email: str) -> User:
    user = User.objects(email=email).first()
    return user

def find_account_by_user_id(user_id: int) -> User:
    user = User.objects(user_id=user_id).first()
    return user