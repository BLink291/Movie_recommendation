import datetime
import mongoengine


class Movie(mongoengine.Document):
    movie_id = mongoengine.IntField(unique=True, primary_key=True)
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
        'collection': 'movies'
    }
