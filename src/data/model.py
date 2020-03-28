import datetime
import mongoengine


class User(mongoengine.Document):
    id = mongoengine.IntField(primary_key= True)
    name = mongoengine.StringField(required=False)
    email = mongoengine.EmailField(required=False)
    pswd = mongoengine.StringField(required=False)
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    admin = mongoengine.BooleanField(default=False)
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
    id = mongoengine.IntField(primary_key=True)
    name = mongoengine.StringField(required=True)
    release_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    vote_count = mongoengine.IntField(default=0)
    vote_avg = mongoengine.FloatField(default=0)
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
    movie_id = mongoengine.IntField(required=True)
    user_id = mongoengine.IntField(required=True)
    rating = mongoengine.FloatField(required=True)
    timestamp = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'core',
        'collection': 'Ratings'
    }
