import mongoengine
import pandas as pd
from src.account import account as acc
from src.data import service
from src.lib.driver import *
from src.lib.switchlang import switch


def run():
    print(' ****************** Welcome guest **************** ')
    print()
    show_commands()
    while True:
        action = get_option()

        with switch(action) as s:
            s.case('a', add_movie)
            s.case('lm', load_movies)
            s.case('lu', load_users)
            s.case('lr', load_ratings)

            s.case('s', service.display_all_movies)
            s.case('info', service.user_info)
            s.case('users', service.user_count)
            s.case('movies', service.movie_count)
            s.case('ratings', service.rating_count)
            s.case('minfo', service.movie_info)

            s.case('r', db_reset)
            s.case('c', acc.create_admin_account)
            s.case('l', acc.log_into_admin)
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
    print('[lm]Add movies from a csv file')
    print('[lu]Add users from a csv file')
    print('[lr]Add ratings from a csv file')
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
        error_msg("You must log in first to add a movie")
        return
    if not acc.active_account.admin:
        error_msg('Only admin can use this feature ')
        return
    name = input("What is the name of movie")
    movie = service.add_movie(name)
    if movie.id:
        success_msg("Successfuly added movie {}".format(movie.name))


def load_movies():
    print(' ************   Add Movies  **************** ')
    # if not acc.active_account:
    #     error_msg("You must log in first to add movies")
    #     return
    # if not acc.active_account.admin:
    #     error_msg('Only admin can use this feature ')
    #     return

    while True:
        try:
            # file_path = input("Enter full path of movie file")
            # movies = pd.read_csv(file_path, low_memory=False)
            # file_path = input("Enter full path of credits file")
            # credit = pd.read_csv(file_path, low_memory=False)
            # file_path = input("Enter full path of keywords file")
            # keywords = pd.read_csv(file_path, low_memory=False)
            # file_path = input("Enter full path of links file")
            # links = pd.read_csv(file_path, low_memory=False)

            movies = pd.read_csv('D:\development\dataset\movies_metadata.csv', low_memory=False)
            credit = pd.read_csv('D:\development\dataset\credits.csv')
            keywords = pd.read_csv('D:\development\dataset\keywords.csv')
            links = pd.read_csv('D:\development\dataset\links.csv')
            cleaned_data = service.data_clean(movies, credit, keywords, links)

            cleaned_data = cleaned_data.rename(columns={"title": "name", "movieId": "id"})
            data_list = cleaned_data.to_dict('records')
            print('************loading data***************')
            service.add_movie_from_list(data_list)
            break
        except Exception as e:
            print(" {}  OR press M to go back to menu : ".format(e))


def load_users():
    print(' ************   Load Users  **************** ')
    if not acc.active_account:
        error_msg("You must log in first")
        return
    if not acc.active_account.admin:
        error_msg('Only admin can use this feature ')
        return
    while True:
        try:
            file_path = input("Enter full path of users file")
            data = pd.read_csv(file_path)
            data_list = data.to_dict('records')
            print('************loading data***************')

            acc.create_accounts_from_list(data_list)
            break
        except Exception as e:
            print(" {}  OR press M to go back to menu : ".format(e))
            if file_path == 'b' or file_path == 'B':
                break


def load_ratings():
    print(' ************   Loading Ratings  **************** ')
    if not acc.active_account:
        error_msg("You must log in first")
        return
    if not acc.active_account.admin:
        error_msg('Only admin can use this feature ')
        return
    while True:
        try:
            file_path = input("Enter full path of ratings file")
            data = pd.read_csv(file_path)
            data_list = data.to_dict('records')
            print('************loading data***************')

            service.add_ratings_from_list(data_list)
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
    if not acc.active_account:
        error_msg("You must log in first")
        return
    if not acc.active_account.admin:
        error_msg('Only admin can clear Database ')
        return

    db = mongoengine.connect(alias='core', name='mrsp')
    db.Movies.drop()

