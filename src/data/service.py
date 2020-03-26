from src.account.account import User, find_account_by_email
from src.data.movie import Movie
from src.data.ratings import Ratings

from typing import List, Optional

import mongoengine
import bson


def get_movie_with_id(movie_id):
    movies = Movie.objects(movie_id=movie_id)
    return movies

def get_movies_for_user(user_id: bson.ObjectId) -> List[Movie]:
    user = User.objects(user_id=user_id).first()
    movies = Movie.objects(movie_id__in=user.movie_ids).all()
    return list(movies)


def review_movie(account, movie_id, given_rating):
    user = find_account_by_email(account.email)
    user.movie_ids.append(movie_id)
    user.save()
    rating = Ratings()
    rating.movie_id = movie_id
    rating.user_id = user.user_id
    rating.rating = given_rating
    rating.save()
