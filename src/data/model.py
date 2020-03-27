import datetime
import mongoengine


class User(mongoengine.Document):
    user_id = mongoengine.IntField(unique=True)
    name = mongoengine.StringField(required=True)
    email = mongoengine.EmailField(required=True)
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    age = mongoengine.IntField(required=False)
    gender = mongoengine.StringField(required=False)
    country = mongoengine.StringField(required=False)
    spoken_languages = mongoengine.ListField(mongoengine.StringField(max_length=50), required=False)

    movie_ids = mongoengine.ListField()

    meta = {
        'db_alias': 'core',
        'collection': 'Users'
    }


class Movie(mongoengine.Document):
    movie_id = mongoengine.IntField(unique=True)
    name = mongoengine.StringField(required=True)
    release_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    vote_count = mongoengine.IntField(required=False)
    vote_avg = mongoengine.FloatField(required=False)
    genres = mongoengine.ListField(mongoengine.StringField(max_length=50), required=False)
    casts = mongoengine.ListField(mongoengine.StringField(max_length=50), required=False)
    spoken_languages = mongoengine.ListField(mongoengine.StringField(max_length=50), required=False)
    country = mongoengine.StringField(required=False)
    adult = mongoengine.BooleanField(default=False)

    meta = {
        'db_alias': 'core',
        'collection': 'Movies'
    }


class Ratings(mongoengine.Document):
    movie_id = mongoengine.ReferenceField(Movie, reverse_delete_rule=1)
    user_id = mongoengine.ReferenceField(User)
    rating = mongoengine.FloatField(required=True)
    timestamp = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'Ratings'
    }
