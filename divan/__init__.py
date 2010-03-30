from django.conf import settings
from couchdb import Server, client

DEFAULT_DIVAN_SERVER = getattr(settings, 'DEFAULT_DIVAN_SERVER', 'http://localhost:5984/')
server = Server(DEFAULT_DIVAN_SERVER)
DEFAULT_DIVAN_DATABASE = getattr(settings, 'DEFAULT_DIVAN_DATABASE', None)
if DEFAULT_DIVAN_DATABASE is not None:
    try:
        db = server[DEFAULT_DIVAN_DATABASE]
    except client.ResourceNotFound:
        db = server.create(DEFAULT_DIVAN_DATABASE)
else:
    db = None
