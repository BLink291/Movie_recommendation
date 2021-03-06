from src.main.program_admin import run as admin
from src.main.program_guest import run as guest
from colorama import Fore
import mongoengine


def db_init():
    mongoengine.register_connection(alias='core', name='mrsp')


def find_user_type():
    print(Fore.WHITE + '****************  Movie Recommendation System  ***********')
    print(Fore.WHITE + '***********************************************************')
    print("A :  Admin Account")
    print("G :  Guest Account")
    print()
    choice = input("Are you a [a]dmin or [g]uest? ")
    if choice == 'a' or choice == 'A':
        return 'admin'
    return 'guest'


def main():
    db_init()

    try:
        while True:
            op = find_user_type()
            if op == 'guest':
                guest()
            elif op == 'admin':
                admin()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()





##END