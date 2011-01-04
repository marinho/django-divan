from couchdb.client import Server
from divan.backends.base import BaseDivanBackend
from divan.timestamps import from_timestamp, to_timestamp

class CouchDB(BaseDivanBackend):
    default_host = 'localhost'
    default_port = '5984'
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
    exclude_keys = ('_id', '_rev')

    def connect(self, database, host, port):
        server = Server('http://%s:%s' % (host, port))
        return server[database]

    def create(self, data):
        doc_id = self.db.create(data)
        document = self.db[doc_id]
        return document

    def update(self, document_id, data):
        document = self.db[document_id]
        for k, v in data.items():
            if v:
                document[k] = v
            else:
                document.pop(k, None)
        self.db[document_id] = document
        return document

    def get_id_for_document(self, document):
        return document['_id']

    def get_document_for_id(self, id):
        return self.db[id]


    def get_document_attr(self, document, field):
        return document[field]
