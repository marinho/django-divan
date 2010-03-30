.. _field-types:

Supported field types
~~~~~~~~~~~~~~~~~~~~~

The following basic field types are supported and provide the expected validation:

    * ``forms.CharField``
    * ``forms.IntegerField``
    * ``forms.FloatField``
    * ``forms.DateField``
    * ``forms.TimeField``
    * ``forms.DateTimeField``
    * ``forms.EmailField``
    * ``forms.FileField``
    * ``forms.ImageField``
    * ``forms.URLField``
    * ``forms.BooleanField``
    * ``forms.IPAddressField``

Additionally, ``forms.ChoiceField`` and ``forms.MultipleChoiceField`` are
available as input methods.  Important to note, however, is that any
:ref:`serialization <serialization>` methods from the field type selected will
be applied to each selected choice.
