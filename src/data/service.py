from src.account.account import User, find_account_by_user_id
from src.data.models import Movies, Ratings
from mongoengine import fields
import pandas as pd
import numpy as np
from ast import literal_eval


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


def get_movie_with_id(movie_id) -> Movies:
    movie = Movies.objects(id=movie_id).first()
    return movie

def top_movies(genres):
    movies = Movies.objects.all()
    li = []
    for mov in movies:
        li.append([mov.id, mov.name, mov.genres, mov.vote_average, mov.vote_count, mov.cast, mov.crew, mov.director, mov.keywords])
    df = pd.DataFrame(li, columns=['id', 'name', 'genres', 'vote_average', 'vote_count', 'cast', 'crew', 'director', 'keywords'])

    df['vote_count'] = df['vote_count'].astype('int')
    df['vote_average'] = df['vote_average'].astype('int')
    df = df[df['vote_average'] != 0]

    c = df['vote_average'].mean()
    m = df['vote_count'].quantile(0.95)
    print(" c = {} and m = {}".format(c, m))

    # qualified = md[(md['vote_count'] >= m) & (md['vote_count'].notnull()) & (md['vote_average'].notnull())][
    #     ['title', 'year', 'vote_count', 'vote_average', 'popularity', 'genres']]
    # qualified['vote_count'] = qualified['vote_count'].astype('int')
    # qualified['vote_average'] = qualified['vote_average'].astype('int')
    # print(qualified.shape)

    def weighted_rating(x):
        v = x['vote_count']
        R = x['vote_average']
        return (v / (v + m) * R) + (m / (m + v) * c)

    q_movies = df.copy().loc[df['vote_count'] >= m]
    print(q_movies.shape)
    q_movies['score'] = q_movies.apply(weighted_rating, axis=1)
    q_movies = q_movies.sort_values('score', ascending=False)
    print(q_movies[['id', 'name', 'vote_count']].head(10))


def display_all_movies():
    movies = Movies.objects.all()
    print("  {0:6}          {1:50}   {2:10}    {3:10}      {4:10}".format("Movie ID", "Movie Name", "avg vote", "release_date", "vote count"))
    i = 0
    for mov in movies:
        i = i+1
        print("  {0:6d}        {1:50} {2:10}     {3:10}   {4:10}".format(mov.id, mov.name, mov.vote_average, mov.release_date, mov.vote_count))
        if i is 20:
            break
    return


def find_ratings_given_by_user(user_id):
    rating = Ratings.objects(user_id=user_id).all()
    return rating


def watched_movies_by_user(user_id):
    ratings = find_ratings_given_by_user(user_id)
    print("You have watched {} movies.".format(len(ratings)))
    print(" {0:6}          {1:45}   {2:3}     {3:60}".format("Movie ID", "Movie Name", "Rating given", "Genres"))
    for vote in ratings:
        movie = get_movie_with_id(vote.movie_id)
        if movie:
            print("  {0:6d}        {1:45}        {2:3}         {3}".format(movie.id, movie.name, vote.rating, movie.genres))
        else:
            print("movie with {} not available".format(vote.movie_id))
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
    movie.vote_average = ((movie.vote_average * movie.vote_count) + given_rating) / (movie.vote_count + 1)
    movie.vote_count = movie.vote_count + 1

    movie.save()
    if timestamp:
        rating.timestamp = timestamp
    rating.save()
    return


def add_movie(name):
    movie = Movies(name=name)
    movie.id = Movies.objects.count() + 1
    movie.save()
    return movie


def data_clean(movies, credits, keywords, links):
    print("Cleaning data ............... ")
    md = movies
    md = md.drop(['belongs_to_collection', 'budget', 'homepage', 'imdb_id', 'original_language',
                  'original_title', 'poster_path', 'production_companies', 'production_countries',
                  'revenue', 'runtime', 'status', 'tagline', 'video', 'popularity'],
                 axis=1)
    md = md.drop([19730, 29503, 35587])

    md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(
        lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

    md['spoken_languages'] = md['spoken_languages'].fillna('[]').apply(literal_eval).apply(
        lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

    md['release_year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(
        lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

    md['id'] = md['id'].astype('int')
    keywords['id'] = keywords['id'].astype('int')
    credits['id'] = credits['id'].astype('int')
    md = md.merge(credits, on='id')
    md = md.merge(keywords, on='id')
    md['keywords'] = md['keywords'].apply(literal_eval)

    def get_keywords(x):  # x is list of dictionary
        li = []
        for i in x:
            li.append(i['name'])
        return li
    md['keywords'] = md['keywords'].apply(get_keywords)

    md['crew'] = md['crew'].apply(literal_eval)

    def get_director(x):  # x is list of dictionary
        for i in x:
            if i['job'] == 'Director':
                return i['name']
        return np.nan

    md['director'] = md['crew'].apply(get_director)

    def get_crew(x):  # x is list of dictionary
        li = []
        for i in x:
            li.append(i['name'])
        return li

    md['crew'] = md['crew'].apply(get_crew)

    md['cast'] = md['cast'].apply(literal_eval)

    def get_cast(x):  # x is list of dictionary
        li = []
        for i in x:
            li.append(i['name'])
        return li

    md['cast'] = md['cast'].apply(get_cast)

    links['tmdbId'] = links['tmdbId'].fillna('0').astype('int')
    links.drop_duplicates(subset="tmdbId", inplace=True)
    links = links.rename(columns={"tmdbId": "id"})
    md = md.merge(links, on='id')
    md = md.drop(['id', 'imdbId'], axis=1)
    md['overview'] = md['overview'].fillna('').astype('string', errors='raise')
    md['release_date'] = md['release_date'].fillna('').astype('string', errors='raise')
    md['title'] = md['title'].fillna('').astype('string', errors='raise')
    md['vote_average'] = md['vote_average'].fillna(0.0).astype('float', errors='raise')
    md['vote_count'] = md['vote_count'].fillna(0).astype('int', errors='raise')
    md['release_year'] = md['release_year'].fillna('').astype('string', errors='raise')
    md['director'] = md['director'].fillna('').astype('string', errors='raise')
    md['adult'] = md['adult'].fillna('').apply(
        lambda x: True if x == 'True' else False)
    print("Cleaning data successful............... ")
    return md


def add_movie_from_list(list_of_movies):
    try:
        for movie in list_of_movies:
            mov = Movies()
            if get_movie_with_id(movie["id"]):
                # print("Tried to enter duplicate entries:")
                # print("skipping movie {}.".format(movie["name"]))
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
            # if not find_account_by_user_id(rating["userId"]):
            # print("skipping.... user with id {} does not exist.".format(rating["userId"]))
            # continue
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


def movie_info():
    movie_id = input('enter id')
    mov = get_movie_with_id(movie_id)
    print("  {0:6}          {1:50}   {2:3}  {3:60}    {4}".format("Movie ID", "Movie Name", "avg vote", "Genres", "adult"))
    print("  {0:6d}        {1:50} {2:3}  {3}      {4}".format(mov.id, mov.name, mov.vote_average, mov.genres, mov.adult))
    return


def user_count():
    print("{} users in database ".format(User.objects.count()))
    return


def movie_count():
    print("{} movies in database ".format(Movies.objects.count()))
    return


def rating_count():
    print("{} ratings in database ".format(Ratings.objects.count()))
    return
