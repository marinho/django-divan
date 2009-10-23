from datetime import date, datetime, time
from django.conf import settings
from django.test import TestCase
from couchdb import Server
from django_divan.divan.models import BaseOption
from django_divan.divan.forms import field_and_kwargs
from django_divan.example.forms import ExampleOptionForm
from django_divan.example.models import ExampleOption, Example

DEFAULT_COUCH_SERVER = getattr(settings, 'DEFAULT_COUCH_SERVER', 'http://localhost:5984/')


class DivanOptionTestCase(TestCase):
    def test_name_mangling(self):
        option = ExampleOption.objects.create(
            field_name='Admissions Contact Name', 
            field_type='CharField', 
            group='test'
        )
        self.assertEquals(option.key, 'admissions_contact_name')


class CouchFormTestCase(TestCase):
    fixtures = ['form_test']

    def test_unbound_form(self):
        form = ExampleOptionForm()
        for field in form:
            self.assertTrue(field.label in ('Foo bar', 'Baz quux'))
        for field in form.fields.keys():
            self.assertTrue(field in ('foo_bar', 'baz_quux')) 

    def test_initialized_form(self):
        server = Server(DEFAULT_COUCH_SERVER)
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
            self.assertTrue(k in doc, k)
            self.assertEquals(doc[k], v)


class CouchDateTimeFieldTestCase(TestCase):
    fixtures = ['datetime_field_test']

    def test_datetime_field(self):
        now = datetime.now()
        today = now.date()
        timeslot = now.time()
        doc_dict = {
            'foo_bar': 'Spam, spam, spam', 
            'baz_quux': False, 
            'date_and_time': now,
            'date': today,
            'time': timeslot
        }
        form = ExampleOptionForm(doc_dict)
        for k in ('date', 'date_and_time', 'time'):
            self.assertTrue(k in form.fields.keys())
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        for k in ('date', 'date_and_time', 'time'):
            self.assertTrue(isinstance(form.cleaned_data[k], (date, datetime, time)))
        try:
            doc = form.save()
        except TypeError, e:
            self.fail(e)
        obj = Example(document_id=doc.id)
        self.assertEquals(obj.date_and_time, now)
        self.assertEquals(obj.date, today)
        self.assertEquals(obj.time, timeslot)
        
    

class CouchModelTestCase(TestCase):
    def setUp(self):
        ExampleOption.objects.create(field_name='Spam', field_type='CharField', group='meat')
        ExampleOption.objects.create(field_name='Bacon', field_type='BooleanField', group='meat')
        ExampleOption.objects.create(field_name='Eggs', field_type='IntegerField', group='vegetarian')
        ExampleOption.objects.create(field_name='Toast', field_type='FloatField', group='vegetarian')
        ExampleOption.objects.create(field_name='Rice', field_type='FloatField', group='vegan')

    def test_iterate_over_fields(self):
        server = Server(DEFAULT_COUCH_SERVER)
        db = server['example']
        doc_dict = {'spam': 'Spam, spam, spam', 'bacon': False, 'eggs': 5, 'toast': 0.456}
        doc_id = db.create(doc_dict)
        example = Example(db[doc_id])
        for field in example.fields:
            example_option = ExampleOption.objects.get(field_name=field.label)
            self.assertEquals(field.label, example_option.field_name)
        for group, fields in example.groups.iteritems():
            self.assertTrue(group in ('meat', 'vegetarian'))
            self.assertEquals(len(fields), 2)

    def test_doc_has_extra_keys(self):
        server = Server(DEFAULT_COUCH_SERVER)
        db = server['example']
        doc_dict = {'spam': 'Spam, spam, spam', 'bacon': False, 'eggs': 5, 'toast': 0.456, 'juice': 10}
        doc_id = db.create(doc_dict)
        example = Example(db[doc_id])
        self.assertRaises(AttributeError, getattr, example, 'juice')
        self.assertTrue(hasattr(example, 'spam'))

    def test_doc_has_missing_values(self):
        server = Server(DEFAULT_COUCH_SERVER)
        db = server['example']
        doc_dict = {'spam': 'Spam, spam, spam', 'bacon': False, 'eggs': 5}
        doc_id = db.create(doc_dict)
        example = Example(db[doc_id])
        self.assertRaises(AttributeError, getattr, example, 'toast')

    def test_doc_has_attr_but_not_group(self):
        server = Server(DEFAULT_COUCH_SERVER)
        db = server['example']
        doc_dict = {'spam': 'Spam, spam, spam', 'bacon': False, 'eggs': 5, 'toast': 0.456, 'juice': 10, 'rice': 4.4}
        doc_id = db.create(doc_dict)
        example = Example(db[doc_id])
        self.assertFalse(example.groups.has_key('vegan'))
        self.assertTrue(hasattr(example, 'rice'))



class MultipleChoiceFieldTestCase(TestCase):
    fixtures = ['multiple_choice_data']

    def test_multiple_choice_field_creation(self):
        form = ExampleOptionForm()
        for f in ('spam', 'bacon', 'eggs', 'toast'):
            self.assertTrue(f in form.fields.keys())
            field = form.fields[f]
            option = ExampleOption.objects.get(key=f)
            field_class, kwargs = field_and_kwargs[option.input_method]
            if kwargs.has_key('widget'):
                self.assertTrue(isinstance(field.widget, kwargs['widget']))
                self.assertTrue(isinstance(field, field_class))

    def test_multiple_choice_field_serialization(self):
        spam = ExampleOption.objects.get(key='spam').exampleoptionchoice_set.all()[0]
        bacon = ExampleOption.objects.get(key='bacon').exampleoptionchoice_set.all()[0]
        eggs1 = ExampleOption.objects.get(key='eggs').exampleoptionchoice_set.all()[0]
        eggs2 = ExampleOption.objects.get(key='eggs').exampleoptionchoice_set.all()[1]
        toast1 = ExampleOption.objects.get(key='toast').exampleoptionchoice_set.all()[0]
        toast2 = ExampleOption.objects.get(key='toast').exampleoptionchoice_set.all()[1]
        form = ExampleOptionForm({
            'spam': spam.id, 
            'bacon': bacon.id, 
            'eggs': [eggs1.id, eggs2.id], 
            'toast': [toast1.id, toast2.id]
        })
        if not form.is_valid():
            self.fail()
        doc = form.save()
        self.assertEquals(doc['spam'], spam.value)
        self.assertEquals(doc['bacon'], bacon.value)
        self.assertEquals(doc['eggs'], [eggs1.value, eggs2.value])
        self.assertEquals(doc['toast'], [toast1.value, toast2.value])

    def test_multiple_choice_initial_values(self):
        spam = ExampleOption.objects.get(key='spam').exampleoptionchoice_set.all()[0]
        bacon = ExampleOption.objects.get(key='bacon').exampleoptionchoice_set.all()[0]
        eggs1 = ExampleOption.objects.get(key='eggs').exampleoptionchoice_set.all()[0]
        eggs2 = ExampleOption.objects.get(key='eggs').exampleoptionchoice_set.all()[1]
        toast1 = ExampleOption.objects.get(key='toast').exampleoptionchoice_set.all()[0]
        toast2 = ExampleOption.objects.get(key='toast').exampleoptionchoice_set.all()[1]
        data = {
            'spam': spam.id, 
            'bacon': bacon.id, 
            'eggs': [eggs1.id, eggs2.id], 
            'toast': [toast1.id, toast2.id]
        }
        form = ExampleOptionForm(data)
        if not form.is_valid():
            self.fail()
        doc = form.save()
        new_form = ExampleOptionForm(document=doc)
        for k, v in new_form.initial.items():
            self.assertEquals(v, data[k])
