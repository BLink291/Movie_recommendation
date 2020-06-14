import datetime
import mongoengine


class User(mongoengine.Document):
    id = mongoengine.IntField(primary_key=True)
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









##END##