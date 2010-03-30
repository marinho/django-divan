.. _backend-api:

The backend API
===============

Divan provides the ability to swap out backends for different key-value stores.
This means that, if your favorite key-value store doesn't have a supported
backend, you can probably just roll your own.  The backend API makes one big
assumption -- that the Python client for your data store returns documents as
dictionaries.  If not, you will have more work to do than otherwise.

To write a backend API, implement a subclass of
``divan.backends.base.BaseDivanBackend`` with the following class attributes
and methods:

Class attributes
----------------
``default_host``. *Required.*
    The default host for this datastore.  Not defining this will result in a
    ``NotImplementedError``.

``default_port``. *Required.*
    The default port for this datastore.  Not defining this will result in a
    ``NotImplementedError``.

``default_serializers``.
    A dictionary mapping ``FormField`` subclass names to :ref:`serializer
    dictionaries <serialization>` that will be used by default for this
    backend.

``exclude_keys``.
    A tuple of keys to any reference or metadata items that are returned when a
    document is fetched from the data store.  In the CouchDB backend, for
    example, this is set to ``('_id', '_rev',)``.

Methods
-------

Backends are required to implement the following methods.  Not doing so will
result in a ``NotImplementedError`` being raised.

``connect(self, database, host, port)``
    Initiates a connection with the data store and returns the handle to the 
    database object.  This database object will be set as the instance member
    ``db``.

``create(self, data)``
    Creates a new record in the database referenced by ``self.db`` using
    ``data``, which will be a dictionary, and returns the dictionary-like
    object for the record.

``update(self, document_id, data)``
    Updates a record with unique identifier ``document_id`` with ``data``, and
    returns the dictionary-like object for the record.

``get_id_for_document(self, document)``
    Returns an id for the dictionary-like object ``document``.

``get_document_attr(self, document, field)``
    Returns the value from ``document`` for the key ``field``.
