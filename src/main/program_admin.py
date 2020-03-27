import mongoengine
import pandas as pd
from src.lib.driver import *
from src.lib.switchlang import switch
from src.account import account as acc
from src.data import service


def run():
    print(' ****************** Welcome guest **************** ')
    print()
    show_commands()
    while True:
        action = get_option()

        with switch(action) as s:
            s.case('a', add_movie)
            s.case('al', add_movie_from_file)
            s.case('s', service.display_all_movies)

            s.case('r', db_reset)
            s.case('c', acc.create_account)
            s.case('l', acc.log_into_account)
            s.case('m', lambda: 'change_mode')
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)

            s.default(unknown_command)

        acc.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[A]dd a movie')
    print('[AL]dd a movie from a csv file')
    print('[S]how all movies')
    print('[L]og into account')
    print('[C]reate an account')
    print("*****[R]eset Database****")
    print('[M]ain menu')
    print('e[X]it app')
    print()


def add_movie():
    print(' ************   Add a movie   **************** ')
    if not acc.active_account:
        error_msg("You must log in first to review a movie")
        return

    movie_id = input("What will be the  movie ID")
    name = input("What is the name of movie")
    movie = service.add_movie(movie_id, name)
    if movie.id:
        success_msg("Successfuly added movie {}".format(movie.name))


def add_movie_from_file():
    print(' ************   Add a movie   **************** ')
    if not acc.active_account:
        error_msg("You must log in first to review a movie")
        return

    while True:
        try:
            file_path = input("Enter full path of movie file")
            data = pd.read_csv(file_path)
            data = data.rename(columns={"movieId": "movie_id", "title": "name"})
            data_list = data.to_dict('records')
            for dict in data_list:
                dict['genres'] = dict['genres'].split('|')

            service.add_movie_from_list(data_list)
            break
        except Exception as e:
            print(" {}  OR press M to go back to menu : ".format(e))
            if file_path == 'b' or file_path == 'B':
                break

def get_option():
    text = '> '
    if acc.active_account:
        text = f'{acc.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def db_reset():
    db = mongoengine.connect(alias='core', name='mrsp')
    db.drop_database('mrsp')
