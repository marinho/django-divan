.. Divan documentation master file, created by
   sphinx-quickstart on Tue Mar 30 15:06:30 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Divan: user-driven database schemas
===================================

Divan is an application that combines some of the best features of Django
(the forms library, the admin, and the template language) with the flexibility
of key-value stores.  It works something like this:

1. You subclass the ``BaseOption`` model provided by ``divan.models``.
2. You register your subclass with the Django admin application.
3. You, or your users, use this subclass to create "fields" that are mapped to keys
   in your key-value store.
4. You subclass the ``DivanForm`` class provided by ``divan.forms``, with a special
   declaration that ties it to your ``BaseOption`` subclass.
5. Your form class will now have all of the fields that you create in the admin, and
   you write a record in your key-value store when you call ``form.save()``.


Contents:

.. toctree::
   :maxdepth: 1

   installation
   getting-started
   baseoption
   field-types
   multiple-choice
   serialization
   backend-api
