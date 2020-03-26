import datetime
import mongoengine


class User(mongoengine.Document):
    user_id = mongoengine.IntField(unique=True, primary_key=True)
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
