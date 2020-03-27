from src.account import account as acc
from src.data import service
from src.lib.switchlang import switch
from src.lib.driver import *


def run():
    print(' ****************** Welcome guest **************** ')
    print()
    show_options()

    while True:
        action = get_option()

        with switch(action) as s:
            s.case('c', acc.create_account)
            s.case('l', acc.log_into_account)
            s.case('w', recommend)
            s.case('r', rate_movie)
            s.case('y', my_movies)
            s.case('m', lambda: 'change_mode')
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)

            s.default(unknown_command)

        acc.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            acc.log_out()
            return


def show_options():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[W]atch a new movie')
    print('[R]eview a movie')
    print('View [y]our watched movies')
    print('[M]ain menu')
    print('e[X]it app')
    print()


def recommend():
    print(' ************   Recommended movies for you **************** ')


def rate_movie():
    print(' ************   Review a movie   **************** ')
    if not acc.active_account:
        error_msg("You must log in first to review a movie")
        return

    movie_id = input("What is movie ID")
    if not movie_id:
        error_msg("Please enter correct movie ID")
        return
    movie = service.get_movie_with_id(movie_id)
    if not movie:
        error_msg("Please enter correct movie ID")
        return

    rating = float(input('How much would you rate this movie  (between 0 to 5)? '))
    service.review_movie(acc.active_account, movie_id, rating)
    acc.reload_account()
    success_msg('Thanks for rating  {}'.format(movie.name))


def my_movies():
    print(' ************   You have watched these movies  **************** ')
    if not acc.active_account:
        error_msg("You must log in first to review a movie")
        return
    movies = service.get_movies_for_user(acc.active_account.user_id)
    print("You have watched {} movies.".format(len(movies)))
    print(" Movie ID          : Movie name              ")
    for mov in movies:
        print(" {}        :  {} ".format(mov.movie_id, mov.name))


def get_option():
    text = '> '
    if acc.active_account:
        text = f'{acc.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()
