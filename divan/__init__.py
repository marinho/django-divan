from django.conf import settings
from couchdb import Server, client

DEFAULT_COUCH_SERVER = getattr(settings, 'DEFAULT_COUCH_SERVER', 'http://localhost:5984/')
server = Server(DEFAULT_COUCH_SERVER)
DEFAULT_COUCH_DATABASE = getattr(settings, 'DEFAULT_COUCH_DATABASE', None)
if DEFAULT_COUCH_DATABASE is not None:
    try:
        db = server[DEFAULT_COUCH_DATABASE]
    except client.ResourceNotFound:
        db = server.create(DEFAULT_COUCH_DATABASE)
else:
    db = None
