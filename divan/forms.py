from datetime import date, datetime, time
from django import forms
from django.db.models import Q
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.forms.widgets import media_property
from couchdb import Server, client
from divan.models import BaseOption
from divan.timestamps import from_timestamp, to_timestamp

DEFAULT_COUCH_SERVER = getattr(settings, 'DEFAULT_COUCH_SERVER', 
        'http://localhost:5984/')

def create_form_field(option):
    FieldClass = getattr(forms, option.field_type)
    help_text = getattr(option, 'help_text', None)
    if help_text:
        help_text = _(help_text)
    return FieldClass(label=_(option.field_name), required=option.required, 
            help_text=help_text)

def get_saved_fields(model, groups):
    if groups is None:
        queryset = model.objects.all()
    else:
        queryset = model.objects.filter(group__in=groups)
    fields = [
        (field.key, create_form_field(field)) 
        for field in queryset.order_by('group', 'order')
    ]
    return SortedDict(fields)

def save_document(form, document_id, fields=None):
    cleaned_data = form.cleaned_data
    db = form.database
    #for field_type in [ft[0] for ft in BaseOption.FIELD_TYPE_OPTIONS]:
    #    if hasattr(new_class._divan, 
    for k, v in [(k, form.fields[k]) for k in cleaned_data.keys() if form.fields.has_key(k)]:
        cls_name = v.__class__.__name__
        divan = form._divan
        if hasattr(divan, cls_name) and cleaned_data[k] is not None:
            cleaned_data[k] = getattr(divan, cls_name)(cleaned_data[k])
    if document_id is not None:
        document = db[document_id]
        for k, v in cleaned_data.items():
            if v:
                document[k] = v
        db[document_id] = document
    else:
        doc_id = db.create(cleaned_data)
        document = db[doc_id]
    return document

class SQLFieldsMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(SQLFieldsMetaclass,
                     cls).__new__(cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = getattr(new_class, 'Divan', None)
        if opts is not None:
            new_class._divan = opts() 
            model = opts.model
            groups = getattr(opts, 'groups', None) 
            base_fields = get_saved_fields(model, groups)
            new_class.base_fields = base_fields
            server_address = getattr(opts, 'server', None) or DEFAULT_COUCH_SERVER
            server = Server(server_address)
            db_name = getattr(model._divan, 'database', None) or settings.DEFAULT_COUCH_DATABASE
            for f in ('DateField', 'DateTimeField', 'TimeField'):
                if not hasattr(new_class._divan, f):
                    setattr(new_class._divan, f, to_timestamp)
            try:
                new_class.database = server[db_name]
            except client.ResourceNotFound:
                new_class.database = server.create(db_name)
        return new_class


class BaseCouchForm(forms.BaseForm):
    def __init__(self, data=None, files=None, document=None, initial=None, *args, **kwargs):
        document_data = {}
        if document is None:
            self.document_id = None
        else:
            self.document_id = document['_id']
            for k, v in document.iteritems():
                if k not in ('_id', '_rev'):
                    document_data[k] = v
        if initial is not None:
            document_data.update(initial)
        super(BaseCouchForm, self).__init__(data, files, initial=document_data,
                                            *args, **kwargs)

    def save(self):
        return save_document(self, self.document_id, self.fields)

    def full_clean(self):
        # import pdb; pdb.set_trace()
        super(BaseCouchForm, self).full_clean()
        


class CouchForm(BaseCouchForm):
    __metaclass__ = SQLFieldsMetaclass
