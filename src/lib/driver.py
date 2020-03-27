from colorama import Fore


def unknown_command():
    print("Sorry i didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()