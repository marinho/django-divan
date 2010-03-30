Dependencies
============

Divan requires Django 1.1 or later.  Additionally, it requires that you have
one of the supported key-value stores and the appropriate Python client library
installed.  Currently, this list includes:

1. CouchDB 0.9.x (with couchdb-python_)

If you want to be able to create form fields that use TinyMCE, you also should
install django-tinymce_.

.. _couchdb-python: http://code.google.com/p/couchdb-python/
.. _django-tinymce: http://code.google.com/p/django-tinymce/


Installation
============

Clone the git repository::

    git clone git://github.com/olifantworkshop/django_divan.git 

Either run ``python setup.py install`` or put the django_divan/divan folder
somewhere on your PYTHONPATH. Add 'divan' to the ``INSTALLED_APPS`` in your
settings module.

Add the following settings to your settings module:

``DIVAN_BACKEND``
    Quoted path to the backend wrapper for your key-value store.  Currently,
    the options are ``'divan.backends.couch.CouchDB'``.

``DIVAN_DATABASE``
    Name of the database where the Divan documents will be stored.

All backends are required to define defaults for the following settings.
Depending on your configuration, you may need to set these as well.

``DIVAN_HOST``
    Host where the key-value store is running.

``DIVAN_PORT``
    Port where the key-value store is running.

Individual backends may require additional configuration.

