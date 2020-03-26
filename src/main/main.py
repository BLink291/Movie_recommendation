import program_admin
import program_guest
from colorama import Fore
import mongoengine

def find_user_type():
    print(Fore.WHITE + '****************  Movie Recommendation System  ***********')
    print(Fore.WHITE + '***********************************************************')
    print("A :  Admin Account")
    print("U :  Guest Account")
    print()
    choice = input("Are you a [a]dmin or [u]ser? ")
    if choice == 'u':
        return 'guest'
    return 'admin'


def main():
    db_init()

    try:
        while True:
            if find_user_type() == 'guest':
                program_guest.run()
            else:
                program_admin.run()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()




def db_init():
    mongoengine.register_connection(alias='core', name='mrs')