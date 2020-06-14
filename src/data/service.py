from src.account.account import User, find_account_by_user_id
from src.data.models import Movies, Ratings
from mongoengine import fields
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity

from ast import literal_eval


def get_movie_with_id(movie_id) -> Movies:
    movie = Movies.objects(id=movie_id).first()
    return movie


def movie_info():
    movie_id = input('enter id')
    mov = get_movie_with_id(movie_id)
    print("  {0:6}          {1:50}   {2:3}  {3:60}    {4}".format("Movie ID", "Movie Name", "avg vote", "Genres",
                                                                  "adult"))
    print(
        "  {0:6d}        {1:50} {2:3}  {3}      {4}".format(mov.id, mov.name, mov.vote_average, mov.genres, mov.adult))
    return


def data_clean(md, credit, keywords, links):
    print("Cleaning data ............... ")

    # Required
    # id, title, genres, overview, release_date, spoken_languages, crew, cast vote_average, vote_count

    # Not required
    #   'revenue', 'runtime', 'status', 'tagline', 'popularity'
    #   'original_title', 'poster_path', 'production_companies', 'production_countries',
    #  'belongs_to_collection', 'budget', 'homepage', 'imdb_id', 'original_language',

    md = md.drop(['belongs_to_collection', 'budget', 'homepage', 'imdb_id', 'original_language',
                  'original_title', 'poster_path', 'production_companies', 'production_countries',
                  'revenue', 'runtime', 'status', 'tagline', 'video', 'popularity'],
                 axis=1)

    # md = md.drop([19730, 29503, 35587])

    def get_name(x):  # x is list of dictionary
        li = []
        for i in x:
            li.append(i['name'])
        return li

    md['genres'] = md['genres'].apply(literal_eval).apply(get_name)

    md['spoken_languages'] = md['spoken_languages'].apply(literal_eval).apply(get_name)

    md['release_year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(
        lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

    md['id'] = md['id'].astype('int')
    keywords['id'] = keywords['id'].astype('int')
    credit['id'] = credit['id'].astype('int')

    md = md.merge(credit, on='id')
    md = md.merge(keywords, on='id')

    md['keywords'] = md['keywords'].apply(literal_eval).apply(get_name)

    md['crew'] = md['crew'].apply(literal_eval)

    def get_director(x):  # x is list of dictionary
        for i in x:
            if i['job'] == 'Director':
                return i['name']
        return np.nan

    md['director'] = md['crew'].apply(get_director)

    md['crew'] = md['crew'].apply(get_name())

    md['cast'] = md['cast'].apply(literal_eval).apply(get_name)

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

    # md['release_year'] = md['release_year'].fillna('').astype('string', errors='raise')

    md['director'] = md['director'].fillna('').astype('string', errors='raise')
    md['adult'] = md['adult'].fillna('').apply(
        lambda x: True if x == 'True' else False)

    print("Cleaning data successful............... ")
    return md

# display top charts


def top_movies(genres=None):

    # return  list of movies object
    movies = Movies.objects.all()
    li = []
    for mov in movies:
        li.append([mov.id, mov.name, mov.genres, mov.vote_average, mov.vote_count])
    df = pd.DataFrame(li, columns=['id', 'name', 'genres', 'vote_average', 'vote_count'])

    if genres:  # if user has specified genres then modify dataframe
        s = df.apply(lambda x: pd.Series(x['genres']), axis=1).stack().reset_index(level=1, drop=True)
        s.name = 'genre'
        gen_md = df.drop('genres', axis=1).join(s)
        df = gen_md[gen_md['genre'].isin(genres)]
        df = df.drop_duplicates(subset="id")

    df['vote_count'] = df['vote_count'].astype('int')
    df['vote_average'] = df['vote_average'].astype('int')

    c = df['vote_average'].mean()
    m = df['vote_count'].quantile(0.95)

    def weighted_rating(x):
        v = x['vote_count']
        R = x['vote_average']
        return (v / (v + m) * R) + (m / (m + v) * c)

    filtered_movies = df.copy().loc[df['vote_count'] >= m]

    filtered_movies['score'] = filtered_movies.apply(weighted_rating, axis=1)

    filtered_movies = filtered_movies.sort_values('score', ascending=False)

    print(filtered_movies[['id', 'name']].head(10))


def recommendation(user_id):
    movies = Movies.objects.all()
    li = []
    for mov in movies:
        li.append([mov.id, mov.name, mov.genres, mov.vote_average, mov.vote_count, mov.cast, mov.crew, mov.director,
                   mov.keywords])

    df = pd.DataFrame(li, columns=['id', 'name', 'genres', 'vote_average', 'vote_count', 'cast', 'crew', 'director',
                                   'keywords'])

    df['cast'] = df['cast'].apply(lambda x: x[:3] if len(x) >= 3 else x)

    df['cast'] = df['cast'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
    df['director'] = df['director'].astype('str').apply(lambda x: str.lower(x.replace(" ", "")))
    df['director'] = df['director'].apply(lambda x: [x, x, x])

    # extract most frequent keywords from whole database
    freq_keywords = df.apply(lambda x: pd.Series(x['keywords']), axis=1).stack().reset_index(level=1, drop=True)
    freq_keywords.name = 'keyword'
    freq_keywords = freq_keywords.value_counts()
    freq_keywords = freq_keywords[freq_keywords > 1]

    stemmer = SnowballStemmer('english')

    def filter_keywords(x):
        words = []
        for i in x:
            if i in freq_keywords:
                words.append(i)
        return words

    df['keywords'] = df['keywords'].apply(filter_keywords)
    df['keywords'] = df['keywords'].apply(lambda x: [stemmer.stem(i) for i in x])
    df['keywords'] = df['keywords'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])

    df['text'] = df['keywords'] + df['cast'] + df['director'] + df['genres']
    df['text'] = df['text'].apply(lambda x: ' '.join(x))

    # df = df.sort_values('vote_average', ascending=True)
    #
    # # df = df.iloc[10000:, ]

    cv = CountVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
    count_matrix = cv.fit_transform(df['text'])

    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    def recommend(idx):
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:26]
        movie_indices = [i[0] for i in sim_scores]

        movies = df.iloc[movie_indices][['name', 'vote_count', 'vote_average']]
        vote_counts = movies['vote_count'].astype('int')
        vote_averages = movies['vote_average'].astype('int')

        c = vote_averages.mean()
        m = vote_counts.quantile(0.60)

        def weighted_rating(x):
            v = x['vote_count']
            R = x['vote_average']
            return (v / (v + m) * R) + (m / (m + v) * c)

        filtered_movies = movies.copy().loc[movies['vote_count'] >= m]

        filtered_movies['score'] = filtered_movies.apply(weighted_rating, axis=1)

        filtered_movies = filtered_movies.sort_values('score', ascending=False).head(10)

        return filtered_movies

    ratings = find_ratings_given_by_user(user_id)
    for r in ratings:
        latest_watched_movie = get_movie_with_id(r.movie_id)
        recommended_movies = recommend(latest_watched_movie.id)
        print(recommended_movies)
        break

    return


def display_all_movies():
    movies = Movies.objects.all()
    print("  {0:6}          {1:50}   {2:10}    {3:10}      {4:10}".format("Movie ID", "Movie Name", "avg vote",
                                                                          "release_date", "vote count"))
    i = 0
    for mov in movies:
        i = i + 1
        print("  {0:6d}        {1:50} {2:10}     {3:10}   {4:10}".format(mov.id, mov.name, mov.vote_average,
                                                                         mov.release_date, mov.vote_count))
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
            print("  {0:6d}        {1:45}        {2:3}         {3}".format(movie.id, movie.name, vote.rating,
                                                                           movie.genres))
        else:
            print("movie with {} not available".format(vote.movie_id))
    return


def review_movie(user_id, movie_id, given_rating):
    user = find_account_by_user_id(user_id)
    user.movie_ids.append(movie_id)
    user.save()

    rating = Ratings()
    rating.movie_id = movie_id
    rating.user_id = user_id
    rating.rating = given_rating
    rating.save()

    movie = get_movie_with_id(movie_id)
    movie.vote_average = ((movie.vote_average * movie.vote_count) + given_rating) / (movie.vote_count + 1)
    movie.vote_count = movie.vote_count + 1
    movie.save()
    return


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


def user_count():
    print("{} users in database ".format(User.objects.count()))
    return


def movie_count():
    print("{} movies in database ".format(Movies.objects.count()))
    return


def rating_count():
    print("{} ratings in database ".format(Ratings.objects.count()))
    return


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



##END##