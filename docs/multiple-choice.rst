.. _multiple-choice:

Dealing with multiple choice fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to support multiple choice fields, you'll have to subclass
``divan.models.OptionChoice`` and add another declaration to the ``Divan``
inner class of your ``BaseOption`` subclass.

::

    class FooOption(BaseOption):
        class Divan:
            database = 'foo'
            choice_related_name = 'bar_set'

    class Bar(OptionChoice):
        option = models.ForeignKey(FooOption)

The name of the foreign key field on ``Bar`` does not matter.  What does matter
is that the ``choice_related_name`` declaration matches the name of the related
manager for that object.

listformat
