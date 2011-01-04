class BaseDivanBackend(object):
    default_host = None
    default_port = None
    default_serializers = {}
    exclude_keys = ()

    def __init__(self, database, host=None, port=None):
        if not (self.default_host and self.default_port):
            raise NotImplementedError('Subclasses of BaseDivanBackend are required to declare a default host and port')
        self.database = database
        self.host = host or self.default_host
        self.port = port or self.default_port
        self.db = self.connect(self.database, self.host, self.port)

    def __getitem__(self, key):
        return self.get_document_for_id(key)

    def get_value_for_field(self, document, field):
        """Fetches a value for a given document and a given field.  Subclasses
        should not override this method; rather, they should override 
        ``get_document_attr``.
        """
        try:
            return self.get_document_attr(document, field)
        except:
            raise AttributeError

    def connect(self, database, host, port):
        "Initiates a connection with the data store.  Subclasses must implement this method."
        raise NotImplementedError()

    def create(self, data):
        raise NotImplementedError()

    def update(self, document_id, data):
        raise NotImplementedError()

    def get_id_for_document(self, document):
        raise NotImplementedError()

    def get_document_for_id(self, id):
        raise NotImplementedError()

    def get_document_attr(self, document, field):
        raise NotImplementedError()
