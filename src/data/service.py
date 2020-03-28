from src.account.account import User, find_account_by_user_id
from src.data.model import Movie, Ratings
from typing import List
import bson
from mongoengine import fields


def update_document(document, data_dict):

    def field_value(field, value):

        if field.__class__ in (fields.ListField, fields.SortedListField):
            return [
                field_value(field.field, item)
                for item in value
            ]
        if field.__class__ in (
            fields.EmbeddedDocumentField,
            fields.GenericEmbeddedDocumentField,
            fields.ReferenceField,
            fields.GenericReferenceField
        ):
            return field.document_type(**value)
        else:
            return value

    [setattr(
        document, key,
        field_value(document._fields[key], value)
    ) for key, value in data_dict.items()]

    return document


def get_movie_with_id(movie_id) -> Movie:
    movie = Movie.objects(id=movie_id).first()
    return movie


def display_all_movies():
    movies = Movie.objects.all()
    print("  {0:6}          {1:50}   {2:60}".format("Movie ID", "Movie Name", "Genres"))
    i = 0
    for mov in movies:
        i = i+1
        if i is 100:
            i = 193781
        print("  {0:6d}        {1:50} {2}".format(mov.id, mov.name, mov.genres))



def find_ratings_given_by_user(user_id):
    rating = Ratings.objects(user_id=user_id).all()
    return rating


def watched_movies_by_user(user_id):
    ratings = find_ratings_given_by_user(user_id)
    print("You have watched {} movies.".format(len(ratings)))
    print(" {0:6}          {1:45}   {2:3}     {3:60}".format("Movie ID", "Movie Name", "Rating given", "Genres"))
    for vote in ratings:
        movie = get_movie_with_id(vote.movie_id)
        print("  {0:6d}        {1:45}        {2:3}         {3}".format(movie.id, movie.name, vote.rating, movie.genres))

    return


def review_movie(user_id, movie_id, given_rating, timestamp=None):
    user = find_account_by_user_id(user_id)
    user.movie_ids.append(movie_id)
    user.save()
    rating = Ratings()
    rating.movie_id = movie_id
    rating.user_id = user_id
    rating.rating = given_rating
    movie = get_movie_with_id(movie_id)
    movie.vote_avg = ((movie.vote_avg * movie.vote_count) + given_rating) / (movie.vote_count + 1)
    movie.vote_count = movie.vote_count + 1

    movie.save()
    if timestamp:
        rating.timestamp = timestamp
    rating.save()
    return


def add_movie(name):
    movie = Movie(name=name)
    movie.id = Movie.objects.count() + 1
    movie.save()
    return movie


def add_movie_from_list(list_of_movies):
    try:
        for movie in list_of_movies:
            mov = Movie()
            if get_movie_with_id(movie["id"]):
                #print("Tried to enter duplicate entries:")
                #print("skipping movie {}.".format(movie["name"]))
                continue
            print("Adding movie {}.".format(movie["name"]))
            update_document(mov, movie)
            mov.save()
    except Exception as e:
        print("error occur in add_movie_from_list {}".format(e))


def add_ratings_from_list(list_of_ratings):
    try:
        for rating in list_of_ratings:
            if not get_movie_with_id(rating["movieId"]):
                print("skipping.... movie with id {} does not exist.".format(rating["movieId"]))
                continue
            #if not find_account_by_user_id(rating["userId"]):
                #print("skipping.... user with id {} does not exist.".format(rating["userId"]))
                #continue
            print("rating.... user with id {} ".format(rating["userId"]))
            review_movie(rating['userId'], rating["movieId"], rating["rating"])
    except Exception as e:
        print("error occur in add_ratings_from_list {}".format(e))


def user_info():
    email = input('enter email')
    user = User.objects(email=email).first()
    print('user_id {} your password; {}, name : {}'.format(user.id, user.pswd, user.name))
    watched_movies_by_user(user.id)
    return


def user_count() :
    print("{} users in database ".format(User.objects.count()))
    return


def movie_count() :
    print("{} movies in database ".format(Movie.objects.count()))
    return


def rating_count() :
    print("{} ratings in database ".format(Ratings.objects.count()))
    return
