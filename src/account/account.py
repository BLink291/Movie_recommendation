from typing import Optional
from src.data.model import User
from src.lib.driver import *

active_account: Optional[User] = None


def create_account():
    global active_account
    print(' ****************** REGISTER **************** ')

    name = input('What is your name? ')
    email = input('What is your email? ').strip().lower()

    old_account = find_account_by_email(email)
    if old_account:
        error_msg(f"ERROR: Account with email {email} already exists.")
        return

    user = User()
    user.name = name
    user.email = email
    user.save()

    active_account = user
    success_msg(f"Created new account with id {active_account.id}.")


def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input('What is your email? ').strip().lower()
    account = find_account_by_email(email)

    if not account:
        error_msg(f'Could not find account with email {email}.')
        return

    global active_account
    active_account = account
    success_msg('Logged in successfully.')


def log_out():
    global  active_account
    active_account = None


def reload_account():
    global active_account
    if not active_account:
        return
    active_account = find_account_by_email(active_account.email)


def find_account_by_email(email: str) -> User:
    user = User.objects(email=email).first()
    return user


def find_account_by_user_id(user_id: int) -> User:
    user = User.objects(user_id=user_id).first()
    return user
