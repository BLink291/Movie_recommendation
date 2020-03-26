import datetime
import mongoengine


class Ratings(mongoengine.Document):
    movie_id = mongoengine.IntField(unique=True, primary_key=True)
    user_id = mongoengine.IntField(unique=True, primary_key=True)
    rating = mongoengine.FloatField(required=True)


    meta = {
        'db_alias': 'core',
        'collection': 'ratings'
    }
