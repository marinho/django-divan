from pymongo.connection import Connection
from pymongo.objectid import ObjectId
from divan.backends.base import BaseDivanBackend
from divan.timestamps import from_timestamp, to_timestamp
from django.conf import settings

class MongoDB(BaseDivanBackend):
    default_host = 'localhost'
    default_port = 27017
    default_serializers = {
        'DateField': {
            'serialize': to_timestamp, 
            'deserialize': from_timestamp
        },
        'DateTimeField': {
            'serialize': to_timestamp, 
            'deserialize': from_timestamp
        },
        'TimeField': {
            'serialize': to_timestamp, 
            'deserialize': from_timestamp
        }
    }
    exclude_keys = ('_id',)

    def connect(self, database, host, port):
        server = Connection(host=host, port=int(port))
        return getattr(server, database)

    @property
    def namespace(self):
        if not getattr(self, '_namespace', None):
            ns = getattr(settings, 'DIVAN_STORE', 'divan')
            self._namespace = getattr(self.db, ns)

        return self._namespace

    def create(self, data):
        doc_id = self.namespace.save(data)
        document = self.namespace.find_one(doc_id)
        return document

    def update(self, document_id, data):
        document = self.namespace.find_one({'_id': document_id})
        for k, v in data.items():
            if v:
                document[k] = v
            else:
                document.pop(k, None)

        self.namespace.save(document)

        return document

    def get_id_for_document(self, document):
        return str(document['_id'])

    def get_document_for_id(self, id):
        return self.namespace.find_one({'_id': id})

    def get_document_attr(self, document, field):
        return document[field] # FIXME?

