from src.account.account import User, find_account_by_email
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
    movie = Movie.objects(movie_id=movie_id).first()
    return movie


def display_all_movies():
    movies = Movie.objects.all()
    print("  {0:6}          {1:50}   {2:60}".format("Movie ID", "Movie Name", "Genres"))
    i = 0
    for mov in movies:
        i = i+1
        print("  {0:6d}        {1:50} {2}".format(mov.movie_id, mov.name, mov.genres))
        if i is 10:
            break


def get_movies_for_user(user_id: bson.ObjectId) -> List[Movie]:
    user = User.objects(user_id=user_id).first()
    movies = Movie.objects(movie_id__in=user.movie_ids).all()
    return list(movies)


def review_movie(account, movie_id, given_rating):
    user = find_account_by_email(account.email)
    user.movie_ids.append(movie_id)
    user.save()
    movie = get_movie_with_id(movie_id)
    movie.save()
    rating = Ratings()
    rating.movie_id = movie.to_dbref()
    rating.user_id = user.to_dbref()
    rating.rating = given_rating
    rating.save()


def add_movie(movie_id, name):
    movie = Movie(movie_id=movie_id, name=name)
    movie.save()
    return movie


def add_movie_from_list(list_of_movies):
    try:
        for movie in list_of_movies:
            mov = Movie()
            if get_movie_with_id(movie["movie_id"]):
                print("Tried to enter duplicate entries:")
                print("skipping movie {}.".format(movie["movie_name"]))
                continue
            print("Adding movie {}.".format(movie["movie_name"]))
            update_document(mov, movie)
            mov.save()
    except Exception as e:
        print(e)