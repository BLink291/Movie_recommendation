import mongoengine
import datetime


class Movies(mongoengine.Document):
    id = mongoengine.IntField(primary_key=True)
    name = mongoengine.StringField(required=True)
    genres = mongoengine.ListField(mongoengine.StringField(max_length=50), required=False)

    release_date = mongoengine.StringField(required=True)  # format("yyyy-mm-dd")
    release_year = mongoengine.StringField(required=True)  # format("yyyy")

    vote_count = mongoengine.IntField(default=0)
    vote_average = mongoengine.FloatField(default=0)

    crew = mongoengine.ListField(mongoengine.StringField(), required=False)
    cast = mongoengine.ListField(mongoengine.StringField(), required=False)
    director = mongoengine.StringField(required=False)

    keywords = mongoengine.ListField(mongoengine.StringField(max_length=50), required=False)
    overview = mongoengine.StringField(required=False)

    spoken_languages = mongoengine.ListField(mongoengine.StringField(max_length=50), required=False)

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



##END##