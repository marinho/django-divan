.. _getting-started:

Getting started
===============

Building a schema
-----------------

Divan operates by letting users define instances of a Django model that are
then mapped to "columns" in a key-value store.  In this manner, a user is able
to change what fields are available in a form (and save data in those fields)
at his leisure.

This is done by subclassing an abstract base model provided by Divan like so::

    from django.contrib import admin
    from django.db import models
    from divan.models import BaseOption

    class FooOption(BaseOption):
        class Divan:
            pass

    admin.site.register(FooOption)

If you now go to the Django admin, you will see that you can create "fields" on
the fly, specifying the ``django.forms.FormField`` subclass, widget, etc.  All
options are explained in detail in the :ref:`BaseOption API documentation
<baseoption>`. 

The ``Divan`` class can also declare a ``choice_related_name`` attribute for
handling multiple choice questions, as explained in the :ref:`Multiple-choice
field documentation <multiple-choice>`.


Forms for the user-defined schema
---------------------------------

To create a form that uses the fields that you have created, simply subclass 
``divan.forms.DivanForm`` and declare an inner ``Divan`` class::

    from divan.forms import DivanForm
    from example.models import FooOption

    class FooForm(DivanForm):
        class Divan:
            model = FooOption
            groups = ['address', 'data']


``DivanForm`` subclasses inherit from ``BaseForm`` with a different metaclass,
so they have all of the goodies you expect from a Django ``Form`` subclass,
including ``is_valid()``, ``is_bound``, ``initial``, etc.  

The fields added to the form will be filtered by the ``FooOption.group``
strings that are declared as a list on the ``group`` attribute of ``Divan``.
If ``group`` is not defined, a field will be created for every instance of
``model``.

They can also be instantiated with an additional keyword argument ``document``,
which should be a dictionary-like object returned from your key-value store.

Like ``ModelForm`` subclasses, ``DivanForm`` subclasses have a ``save()``
method.  If the given instance was instantiated with an argument to the
``document`` parameter, it will update the document in question; otherwise, it
will create a new one.  ``save()`` returns the new or updated document.

Accessing your data in templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Divan provides a wrapper class called ``DivanModel`` that makes it easier to
deal with your documents in templates.  It does not provide database write
capabilities. It simply gives template authors a few convenient accessors.

To use it, subclass ``DivanModel`` like so::
    
    from divan.models import DivanModel
    
    class Foo(DivanModel):
        class Divan:
            schema = FooOption

Now we instantiate ``Foo``, passing it a document retrieved from the data store.

::

    foo = Foo(document)

The resulting instance will have attributes corresponding to each instance of
``FooOption`` that you have created, accessible by their respective ``key``
values. Any other keys that happen to be in the document will not be added to
the object.

You can also iterate over the ``DivanModel``::

    for field in foo:
        print field.label, field

``Foo`` will also have a dictionary of fields grouped by the ``group``
attribute of ``FooOption``, which is aptly named ``groups``.  This allows you to
display large documents in a structured manner in the templates.

:: 

    {% for title, fieldset in document.groups.items %}
        <h3>{{ title }}</h3>
        {% for field in fieldset %}
            <p>{{ field.label }}: {{ field }}</p>
        {% endfor %}
    {% endfor %}
