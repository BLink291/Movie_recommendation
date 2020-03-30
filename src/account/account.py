from src.account.models import User
from src.lib.driver import *

from passlib.context import CryptContext
from typing import Optional


active_account: Optional[User] = None


pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)


def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)


def create_accounts_from_list(data_list):
    try:
        for data in data_list:
            if find_account_by_email(data['email']):
                # print("Tried to enter duplicate entries:")
                #print("skipping user {} with email {}.".format(data["name"], data["email"]))
                continue
            #print("Adding USer {}.".format(data["name"]))
            user = User()
            user.name = data["name"]
            user.email = data["email"]
            user.pswd = encrypt_password(data["pswd"])
            user.id = User.objects.count() + 1
            user.save()
    except Exception as e:
        print("error occur {}".format(e))


def create_account():
    global active_account
    print(' ****************** REGISTER **************** ')

    name = input('What is your name? ')
    email = input('What is your email? ').strip().lower()
    pswd = input('What is your password? ')
    old_account = find_account_by_email(email)
    if old_account:
        error_msg(f"ERROR: Account with email {email} already exists.")
        return

    user = User()
    user.name = name
    user.email = email
    user.pswd = encrypt_password(pswd)
    user.id = User.objects.count() + 1
    user.save()

    active_account = user
    success_msg(f"Created new account with id {active_account.id}.")


def create_admin_account():
    global active_account
    print(' ****************** REGISTER **************** ')

    name = input('What is your name? ')
    email = input('What is your email? ').strip().lower()
    pswd = input('What is your password? ')
    old_account = find_account_by_email(email)
    if old_account:
        error_msg(f"ERROR: Account with email {email} already exists.")
        return

    user = User()
    user.name = name
    user.email = email
    user.pswd = encrypt_password(pswd)
    user.admin = True
    user.id = User.objects.count() + 1
    user.save()

    active_account = user
    success_msg(f"Created new account with id {active_account.id}.")


def log_into_account():
    print(' ****************** LOGIN **************** ')
    global active_account
    email = input('What is your email? ').strip().lower()
    pswd = input('What is your password? ')
    account = find_account_by_email(email)
    if not account:
        error_msg(f'Could not find account with email {email}.')
        return
    if check_encrypted_password(pswd, account.pswd):
        active_account = account
        success_msg('Logged in successfully.')
    else:
        active_account = None
        error_msg('Password entered does not match.')


def log_into_admin():
    print(' ****************** ADMIN LOGIN **************** ')
    global active_account
    email = input('What is your email? ').strip().lower()
    pswd = input('What is your password? ')
    account = find_account_by_email(email)
    if not account:
        error_msg(f'Could not find account with email {email}.')
        return
    if not account.admin:
        error_msg('This is not a admin account please choose guest login. ')
        return

    if check_encrypted_password(pswd, account.pswd):
        active_account = account
        success_msg('Logged in successfully.')
    else:
        active_account = None
        error_msg('Password entered does not match.')


def log_out():
    global active_account
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
    user = User.objects(id=user_id).first()
    return user

