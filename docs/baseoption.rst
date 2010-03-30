.. _baseoption:

The ``BaseOption`` API
======================

``BaseOption`` includes the following fields:

``field_name``
    The human readable name of the field.  Used as the argument to the
    ``label`` parameter of the field constructor.

``field_type``
    User-friendly names that map to one of the ``Field`` subclasses in
    ``django.forms.fields``.  See :ref:`Supported field types <field-types>`.

``input_method``
    Controls a combination of the ``Field`` subclass used (for multiple choice
    values) and widgets applied (TinyMCE, textarea, etc.).

``group``
    String to tag groups of fields.  A future release will include JavaScript
    for auto-completing to ensure consistency across instances.

``key``
    Auto-generated value from ``field_name``, lower-casing the string and
    replacing non-alphanumeric characters with underscores.  When form classes
    are created, the field will be accessible as an attribute with this name.

``required``
    Determines whether or not the field will be required in forms.

``order``
    Secondary sort condition after ``group``.  This is currently useless.  A
    future release will include JavaScript for drag & drop sorting of Option
    instances in the Django admin.

