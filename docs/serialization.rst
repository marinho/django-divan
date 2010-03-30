.. _serialization:

Serialization
=============

Any of the supported field types may have default serializer/deserializer
functions declared on ``DivanForm`` or ``DivanModel`` subclasses.  For example,
you might want to pad ``IntegerField`` values with leading zeros if you are
using Lucene to drive search over CouchDB documents::

    class FooForm(DivanForm):
        class Divan:
            model = FooOption
            IntegerField = {
                'serialize': lambda i: '%015d' % i,
                'deserialize': lambda s: int(s)
            }

Backends can define their own default serialization methods.  This behavior can
be overridden as desired.

