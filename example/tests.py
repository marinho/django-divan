from django.test import TestCase
from couchdb import Server
from django_divan.example.forms import ExampleOptionForm
from django_divan.example.models import ExampleOption

class SimpleTest(TestCase):
    def test_unbound_form(self):
        form = ExampleOptionForm()
        for field in form:
            self.assertTrue(field.label in ('Foo bar', 'Baz quux'))
        for field in form.fields.keys():
            self.assertTrue(field in ('foo_bar', 'baz_quux')) 

    def test_initialized_form(self):
        server = Server('http://localhost:5984/')
        db = server['example']
        doc_dict = {'foo_bar': 'Spam, spam, spam', 'baz_quux': False}
        doc_id = db.create(doc_dict)
        doc = db[doc_id]
        form = ExampleOptionForm(document=doc)
        self.assertEquals(form.initial, doc_dict)

    def test_bound_form_create_doc(self):
        ExampleOption.objects.create(field_name='Foo bar', field_type='CharField', group='test')
        ExampleOption.objects.create(field_name='Baz quux', field_type='BooleanField', group='test')
        doc_dict = {'foo_bar': 'Spam, spam, spam', 'baz_quux': False}
        form = ExampleOptionForm(doc_dict)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        doc = form.save()
        for k, v in doc_dict.items():
            self.assertTrue(k in doc)
            self.assertEquals(doc[k], v)
    
