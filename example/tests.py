from datetime import date, datetime
from django.conf import settings
from django.test import TestCase
from couchdb import Server
from django_divan.example.forms import ExampleOptionForm
from django_divan.example.models import ExampleOption, Example

class CouchFormTestCase(TestCase):
    fixtures = ['form_test.json']

    def test_unbound_form(self):
        form = ExampleOptionForm()
        for field in form:
            self.assertTrue(field.label in ('Foo bar', 'Baz quux'))
        for field in form.fields.keys():
            self.assertTrue(field in ('foo_bar', 'baz_quux')) 

    def test_initialized_form(self):
        server = Server(settings.DEFAULT_COUCH_SERVER)
        db = server['example']
        doc_dict = {'foo_bar': 'Spam, spam, spam', 'baz_quux': False}
        doc_id = db.create(doc_dict)
        doc = db[doc_id]
        form = ExampleOptionForm(document=doc)
        self.assertEquals(form.initial, doc_dict)

    def test_bound_form_create_doc(self):
        doc_dict = {'foo_bar': 'Spam, spam, spam', 'baz_quux': False}
        form = ExampleOptionForm(doc_dict)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        doc = form.save()
        for k, v in doc_dict.items():
            self.assertTrue(k in doc)
            self.assertEquals(doc[k], v)


class CouchDateTimeFieldTestCase(TestCase):
    fixtures = ['form_test.json']

    def test_datetime_field(self):
        ExampleOption.objects.create(field_name='Date and time', field_type='DateTimeField', group='blah')
        now = datetime.now()
        doc_dict = {'foo_bar': 'Spam, spam, spam', 'baz_quux': False, 'date_and_time': now}
        form = ExampleOptionForm(doc_dict)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        try:
            doc = form.save()
        except TypeError:
            self.fail()
        obj = CouchModel(document_id=doc.id)
        self.assertEquals(obj.date_and_time, now)
        


    

class CouchModelTestCase(TestCase):
    def setUp(self):
        ExampleOption.objects.create(field_name='Spam', field_type='CharField', group='meat')
        ExampleOption.objects.create(field_name='Bacon', field_type='BooleanField', group='meat')
        ExampleOption.objects.create(field_name='Eggs', field_type='IntegerField', group='vegetarian')
        ExampleOption.objects.create(field_name='Toast', field_type='FloatField', group='vegetarian')

    def test_iterate_over_fields(self):
        server = Server(settings.DEFAULT_COUCH_SERVER)
        db = server['example']
        doc_dict = {'spam': 'Spam, spam, spam', 'bacon': False, 'eggs': 5, 'toast': 0.456}
        doc_id = db.create(doc_dict)
        example = Example(doc_id)
        for field in example.fields:
            example_option = ExampleOption.objects.get(field_name=field.label)
            self.assertEquals(getattr(example, example_option.key).label, example_option.field_name)
        for group, fields in example.groups.iteritems():
            self.assertTrue(group in ('meat', 'vegetarian'))
            self.assertEquals(len(fields), 2)

    def test_doc_has_extra_keys(self):
        server = Server(settings.DEFAULT_COUCH_SERVER)
        db = server['example']
        doc_dict = {'spam': 'Spam, spam, spam', 'bacon': False, 'eggs': 5, 'toast': 0.456, 'juice': 10}
        doc_id = db.create(doc_dict)
        example = Example(doc_id)
        self.assertRaises(AttributeError, getattr, example, 'juice')
        self.assertTrue(hasattr(example, 'spam'))

    def test_doc_has_missing_values(self):
        server = Server(settings.DEFAULT_COUCH_SERVER)
        db = server['example']
        doc_dict = {'spam': 'Spam, spam, spam', 'bacon': False, 'eggs': 5}
        doc_id = db.create(doc_dict)
        example = Example(doc_id)
        self.assertRaises(AttributeError, getattr, example, 'toast')
